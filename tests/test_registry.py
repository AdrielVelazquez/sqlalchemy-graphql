from sqlalchemy_epoxy.sqlalchemy import EpoxySQLAlchemy

from tests import R


def test_registry():
    esql = EpoxySQLAlchemy()
    esql.register(R)
    import pdb; pdb.set_trace()

