from epoxy import TypeRegistry

from sqlalchemy_graphql.epoxy import EpoxySQLAlchemy

R = TypeRegistry()
esql = EpoxySQLAlchemy()
esql.register(R)

from tests import graphql_models
