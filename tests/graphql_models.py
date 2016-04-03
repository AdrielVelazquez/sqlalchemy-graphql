from tests import R, esql
from tests.sample_models import ChildModel as BaseChildModel, ParentModel as BaseParentModel, session

from sqlalchemy_graphql.epoxy.utils import add_query_args
from sqlalchemy_graphql.epoxy.query import resolve_sqlalchemy

model_args = add_query_args({"id": R.Int, "name": R.String, "ids": R.Int.List}, esql.query_args)


class ParentModel(R.Implements.FuncBase):
    id = R.Int
    name = R.String
    children = R.ChildModel.List(args=model_args)

    def resolve_children(self, obj, args, info):
        return resolve_sqlalchemy(obj, args, info, BaseChildModel, query=obj.children)


class ChildModel(R.Implements.FuncBase):
    id = R.Int
    name = R.String
    parent = R.ParentModel(args=model_args)

    def resolve_parent(self, obj, args, info):
        return resolve_sqlalchemy(obj, args, info, BaseParentModel, query=obj.parent)


class Query(R.ObjectType):
    parent_model = R.ParentModel(args=model_args)
    child_model = R.ChildModel(args=model_args)
    parent_models = R.ParentModel.List(args=model_args)
    child_models = R.ChildModel.List(args=model_args)
    additional_filters = R.ParentModel(args=model_args)

    def resolve_parent_model(self, obj, args, info):
        query = session.query(BaseParentModel)
        return resolve_sqlalchemy(obj, args, info, BaseParentModel, query=query, single=True)

    def resolve_child_model(self, obj, args, info):
        query = session.query(BaseChildModel)
        return resolve_sqlalchemy(obj, args, info, BaseChildModel, query=query, single=True)

    def resolve_parent_models(self, obj, args, info):
        query = session.query(BaseParentModel)
        return resolve_sqlalchemy(obj, args, info, BaseParentModel, query=query)

    def resolve_child_models(self, obj, args, info):
        query = session.query(BaseChildModel)
        return resolve_sqlalchemy(obj, args, info, BaseChildModel)

    def resolve_additional_filters(self, obj, args, info):
        query = session.query(BaseParentModel)
        additional_filters = [BaseParentModel.name == "Adriel"]
        return resolve_sqlalchemy(obj, args, info, BaseParentModel,
            query=query, single=True, additional_filters=additional_filters
        )
