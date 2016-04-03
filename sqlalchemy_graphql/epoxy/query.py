from flask_sqlalchemy import BaseQuery
from sqlalchemy import inspect, func
from sqlalchemy.orm.query import Query
from graphql.core.error import GraphQLError

from sqlalchemy_graphql.epoxy.custom_scalar_types import to_delimiter_case
from sqlalchemy_graphql.epoxy.utils import resolve_keyed_tuples


def get_dict_args(args):
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
def resolve_sqlalchemy(obj, args, info, model, query=None, additional_filters=None, single=False):
    '''
    Generic Function for resolving a single alchemy model.
    '''
    args, before, after, order, first, last, group = get_dict_args(args)
    if additional_filters:
        query = query.filter(*additional_filters)
    query = add_filters(obj, args, info, model, query)
    query, group = visit_fields(obj, args, info, model, query, group)
    query = add_order(
        obj, args, info, model, query, before, after, order, first, last, group)
    if single:
        return query.first()
    else:
        if isinstance(query, BaseQuery) or isinstance(query, Query):
            return query.all()
        return query


def visit_fields(obj, args, info, model, query, groups):
    selections = info.field_asts[0].selection_set.selections
    additional_columns = []
    for field in selections:
        if field.name.value == "func":
            add_col, group = visit_func(model, field)
            additional_columns.extend(add_col)
            groups = group + groups
        elif field.name.value == "count":
            additional_columns.append(visit_count(model, field))
    if additional_columns:
        return query.add_columns(*additional_columns), groups
    return query, groups


def visit_func(model, field):
    target_column, operation = field.arguments
    func_name = operation.value.value
    target_name = to_delimiter_case(target_column.value.value)
    if func_name == "distinct":
        return [], [target_name]
    agg_func = getattr(func, func_name)
    return [agg_func(getattr(model, target_name)).label(
        "{}_{}".format(target_name, func_name))], []


def visit_count(model, field):
    if field.arguments:
        distinct = field.arguments[0]
        distinct_name = distinct.name.value
        on_target_name = to_delimiter_case(distinct.value.value)
        dis_func = getattr(func, distinct_name)
        return func.count(dis_func(getattr(model, on_target_name))
                          ).label("{}_{}_{}".format(on_target_name, distinct_name, field.name.value))
    return func.count(model).label("count")


def add_filters(obj, args, info, model, query):
    for key, value in args.items():
        if isinstance(value, dict):
            query = query.filter(*get_dict_filter(query, model, key, value))
        elif isinstance(value, list):
            query = get_list_filters(query, model, key, value)
        else:
            query = query.filter(getattr(model, key) == value)
    return query


def get_dict_filter(query, model, key, values):
    if key == "like":
        return [getattr(model, k).like(v) for k, v in values.items()]
    elif key == "match":
        return [getattr(model, k).match(v) for k, v in values.items()]
    elif key == "options":
        return [func.options(*[getattr(model, k) == v for k, v in values.items()])]


def get_list_filters(query, model, key, values):
    if hasattr(model, key[:-1]):
        return query.filter(getattr(model, key[:-1]).in_(values))
    return query.filter(getattr(model, key).contains(values))


def add_order(obj, args, info, model, query, before, after, order, first, last, group, distinct_group=None):
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
