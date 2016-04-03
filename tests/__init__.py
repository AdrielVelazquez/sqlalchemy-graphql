from epoxy import TypeRegistry

from sqlalchemy_epoxy.sqlalchemy import EpoxySQLAlchemy

R = TypeRegistry()
esql = EpoxySQLAlchemy()
esql.register(R)

from tests import graphql_models
