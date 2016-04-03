from epoxy import TypeRegistry

from sqlalchemy_epoxy.sqlalchemy import EpoxySQLAlchemy


def test_registry():
    tester_registry = TypeRegistry()
    esql = EpoxySQLAlchemy()
    esql.register(tester_registry)
    assert "DictionaryType" in tester_registry._registered_types.keys()
    assert "CamelCaseString" in tester_registry._registered_types.keys()
    for key, value in esql.query_args.items():
        assert value is not None
