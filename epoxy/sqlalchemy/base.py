from flask_sqlalchemy import BaseQuery as FlaskBaseQuery
from sqlalchemy import inspect, func
from graphql.core.error import GraphQLError

from app import R, db
from app.graphql.custom_scalar_types import to_delimiter_case
from app.graphql.utils import resolve_keyed_tuples

__all__ = ["BaseQuery", "Base"]


class Base(R.Interface):

    '''
    Common Query Class
    '''
    func = R.DictionaryType(args={"field": R.CamelCaseString, "op": R.String})
    count = R.Int(args={"distinct": R.CamelCaseString})

    def resolve_func(self, obj, args, info):
        if args.get("op") == "distinct":
            return getattr(obj, args.get("field"))
        target = "{}_{}".format(args.get("field"), args.get("op"))
        return getattr(obj, target)

    def resolve_count(self, obj, args, info):
        target = "count"
        if args.get("distinct"):
            target = "{}_{}_{}".format(args.get("distinct"), "distinct", "count")
        return getattr(obj, target)


class BaseQuery:

    COLUMN_MAP = {
        "Integer": R.Int,
        "Float": R.Float,
        "ListOfStrings": R.String.List,
        "String": R.String,
        "Unicode": R.String,
        "UnicodeText": R.String,
        "Text": R.String,
        "TEXT": R.String,
        "CHAR": R.String,
        "VARCHAR": R.String,
        "TIMESTAMP": R.DateTime,
        "DateTime": R.DateTime,
        "Boolean": R.Boolean,
        "Enum": R.CountryEnum,
        "ENUM": R.String,
        "BigInteger": R.Int
    }

    def get_dict_args(self, args):
        before = args.pop("before", None)
        after = args.pop("after", None)
        order = args.pop("order", [])
        if (before or after) and not order:
            raise GraphQLError("order is required for before and after")
        first = args.pop("first", None)
        last = args.pop("last", None)
        group = args.pop("group", [])
        return args, before, after, order, first, last, group

    @resolve_keyed_tuples
    def resolve_sqlalchemy(self, obj, args, info, model, related=None, additional_filters=None, single=False):
        '''
        Generic Function for resolving a single alchemy model
        '''
        args, before, after, order, first, last, group = self.get_dict_args(args)
        if related:
            query = related
        else:
            query = model.query
        if additional_filters:
            query = query.filter(*additional_filters)
        query = self.add_filters(obj, args, info, model, query)
        query, group = self.visit_fields(obj, args, info, model, query, group)
        query = self.add_order(
            obj, args, info, model, query, before, after, order, first, last, group)
        if single:
            return query.first()
        elif related:
            if isinstance(query, FlaskBaseQuery):
                return query.all()
            return query
        return query.all()

    def visit_fields(self, obj, args, info, model, query, groups):
        selections = info.field_asts[0].selection_set.selections
        additional_columns = []
        for field in selections:
            if field.name.value == "func":
                add_col, group = self.visit_func(model, field)
                additional_columns.extend(add_col)
                groups = group + groups
            elif field.name.value == "count":
                additional_columns.append(self.visit_count(model, field))
        if additional_columns:
            return query.add_columns(*additional_columns), groups
        return query, groups

    def visit_func(self, model, field):
        target_column, operation = field.arguments
        func_name = operation.value.value
        target_name = to_delimiter_case(target_column.value.value)
        if func_name == "distinct":
            return [], [target_name]
        agg_func = getattr(func, func_name)
        return [agg_func(getattr(model, target_name)).label(
            "{}_{}".format(target_name, func_name))], []

    def visit_count(self, model, field):
        if field.arguments:
            distinct = field.arguments[0]
            distinct_name = distinct.name.value
            on_target_name = to_delimiter_case(distinct.value.value)
            dis_func = getattr(func, distinct_name)
            return func.count(dis_func(getattr(model, on_target_name))
                ).label("{}_{}_{}".format(on_target_name, distinct_name, field.name.value))
        return func.count(model).label("count")

    def add_filters(self, obj, args, info, model, query):
        for key, value in args.items():
            if key == "tier1":
                query = self.get_tier_label_filter(query, model, value)
            elif isinstance(value, dict):
                query = query.filter(*self.get_dict_filter(query, model, key, value))
            elif isinstance(value, list):
                query = self.get_list_filters(query, model, key, value)
            else:
                query = query.filter(getattr(model, key) == value)
        return query

    def get_tier_label_filter(self, query, model, value):
        sub_query = db.session.query(WeightedLabel.child_id)
        sub_query = sub_query.group_by(WeightedLabel.child_id).subquery("sub_query")
        tier_query = db.session.query(model.id).join(WeightedLabel, model.id == WeightedLabel.parent_id)
        tier_query = tier_query.filter(model.id != WeightedLabel.child_id, ~model.id.in_(sub_query))
        tier_query = tier_query.filter(model.label_type == "target")
        tier_query = tier_query.group_by(model.id)
        tier_1_ids = [tier_label.id for tier_label in tier_query]
        if value == True:
            return query.filter(model.id.in_(tier_1_ids))
        return query.filter(~model.id.in_(tier_1_ids))

    def get_dict_filter(self, query, model, key, values):
        if key == "like":
            return [getattr(model, k).like(v) for k, v in values.items()]
        elif key == "match":
            return [getattr(model, k).match(v) for k, v in values.items()]
        elif key == "options":
            return [func.options(*[getattr(model, k) == v for k, v in values.items()])]

    def get_list_filters(self, query, model, key, values):
        if hasattr(model, key[:-1]):
            return query.filter(getattr(model, key[:-1]).in_(values))
        return query.filter(getattr(model, key).contains(values))

    def add_order(self, obj, args, info, model, query,
            before, after, order, first, last, group, distinct_group=None):
        if order:
            order = [getattr(model, col) for col in order]
        model_mapper = inspect(model)
        if before:
            query = query.filter(order[0] < before)
        if after:
            query = query.filter(order[0] > after)
        if group:
            query = query.group_by(*[getattr(model, grp) for grp in group])
        if order and last:
            order = [col.desc() for col in order]
            query = query.order_by(*order).limit(last)
        elif order and first:
            order = [col.asc() for col in order]
            query = query.order_by(*order).limit(first)
        elif order:
            query = query.order_by(*order)
        elif last:
            query = query.order_by(
                *[pk.desc() for pk in list(model_mapper.primary_key)]).limit(last)
        elif first:
            query = query.order_by(
                *[pk.asc() for pk in list(model_mapper.primary_key)]).limit(first)
        return query
