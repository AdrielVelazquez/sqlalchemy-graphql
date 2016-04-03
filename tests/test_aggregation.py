from graphql.core import graphql

from tests.sample_models import ParentModel, session
from tests import R


def test_normal_querying():
    test_parent_1 = ParentModel(name="Adriel")
    test_parent_2 = ParentModel(name="Carolina")
    session.add(test_parent_1)
    session.add(test_parent_2)
    session.commit()
    schema = R.Schema(R.Query)

    query = "{parentModels {id, name}}"
    results = graphql(schema, query)
    assert len(results.data.get("parentModels")) == 2
    session.delete(test_parent_2)
    session.delete(test_parent_1)
    session.commit()


def test_aggregation():
    test_parent_1 = ParentModel(name="Adriel")
    test_parent_2 = ParentModel(name="Carolina")
    session.add(test_parent_1)
    session.add(test_parent_2)
    session.commit()
    schema = R.Schema(R.Query)
    query = '{parentModel {idSum: func(field:"id", op:"sum")}}'
    results = graphql(schema, query)
    value = test_parent_1.id + test_parent_2.id
    assert results.data['parentModel']['idSum'] == value
