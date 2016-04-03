from graphql.core import graphql

from tests.sample_models import ParentModel, session, ChildModel
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

    test_child_1 = ChildModel(name="Oona", parent_id=test_parent_1.id)
    session.add(test_child_1)
    session.commit()
    query = "{childModel {id,name, parent {id, name}}}"
    results = graphql(schema, query)
    expected_results = {
        "childModel": {
            "id": test_child_1.id,
            "name": "Oona",
            "parent": {
                "id": test_parent_1.id,
                "name": test_parent_1.name
            }
        }
    }
    assert results.data == expected_results
    query = '{additionalFilters (name:"Someting"){id,name}'
    assert len(results.errors) == 0
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
    session.delete(test_parent_2)
    session.delete(test_parent_1)
    session.commit()


def test_filters():
    test_parent_1 = ParentModel(name="Adriel")
    test_parent_2 = ParentModel(name="Carolina")
    test_parent_3 = ParentModel(name="Cotu")
    session.add(test_parent_1)
    session.add(test_parent_2)
    session.add(test_parent_3)
    session.commit()
    schema = R.Schema(R.Query)
    query = '{{parentModels (ids:[{}, {}]) {{id, name}} }}'.format(test_parent_1.id, test_parent_2.id)
    results = graphql(schema, query)
    expected_results = {
        'parentModels': [
            {'name': 'Adriel', 'id': test_parent_1.id}, {'name': 'Carolina', 'id': test_parent_2.id}
        ]
    }
    assert results.data == expected_results
    query = '{{parentModels (ids:[{}, {}], name:"Adriel") {{id, name}} }}'.format(test_parent_1.id, test_parent_2.id)
    results = graphql(schema, query)
    expected_results = {
        'parentModels': [
            {'name': 'Adriel', 'id': test_parent_1.id}
        ]
    }
    assert results.data == expected_results
    session.delete(test_parent_3)
    session.delete(test_parent_2)
    session.delete(test_parent_1)
    session.commit()


def test_distinct_count():
    test_parent_1 = ParentModel(name="Adriel")
    test_parent_2 = ParentModel(name="Adriel")
    session.add(test_parent_1)
    session.add(test_parent_2)
    session.commit()
    schema = R.Schema(R.Query)
    query = '{parentModels (group:["name"]){distinctName: count(distinct:"name")}}'
    results = graphql(schema, query)
    expected_results = {'parentModels': [{'distinctName': 1}]}
    assert results.data == expected_results
    query = '{parentModels {distinctName: count(distinct:"name")}}'
    results = graphql(schema, query)
    expected_results = {'parentModels': [{'distinctName': 1}]}
    assert results.data == expected_results
    session.delete(test_parent_2)
    session.delete(test_parent_1)
    session.commit()


def test_count_sanity():
    from sqlalchemy_epoxy.sqlalchemy.query import visit_count
    from sqlalchemy.sql.elements import Label
    fields = type("something", (), {"arguments": None})
    returned = visit_count(ParentModel, fields())
    assert isinstance(returned, Label)


def test_ordering():
    test_parent_1 = ParentModel(name="Adriel")
    test_parent_2 = ParentModel(name="Carolina")
    test_parent_3 = ParentModel(name="Cotu")
    session.add(test_parent_1)
    session.add(test_parent_2)
    session.add(test_parent_3)
    session.commit()
    schema = R.Schema(R.Query)
    query = '{parentModel (after: "Carolina", order:["name"]) {id, name}}'
    results = graphql(schema, query)
    expected_results = {'parentModel': {'id': test_parent_3.id, 'name': 'Cotu'}}
    assert results.data == expected_results

    query = '{parentModels (first: 2, after:"Adriel", order:["name"]){id, name}}'
    results = graphql(schema, query)
    expected_results = {
        'parentModels': [
            {'name': 'Carolina', 'id': test_parent_2.id}, {'name': 'Cotu', 'id': test_parent_3.id}
        ]
    }
    assert results.data == expected_results
    query = '{parentModels (first: 2, before:"Adriel", order:["name"]){id, name}}'
    results = graphql(schema, query)
    expected_results = {
        'parentModels': []
    }
    assert results.data == expected_results
    query = '{parentModels (first: 2, before:"Adriel"){id, name}}'
    results = graphql(schema, query)
    assert len(results.errors) == 1
    query = '{parentModels (last: 2, after:"Adriel", order:["name"]){id, name}}'
    results = graphql(schema, query)
    expected_results = {
        'parentModels': [
            {'name': 'Cotu', 'id': test_parent_3.id}, {'name': 'Carolina', 'id': test_parent_2.id}
        ]
    }
    assert results.data == expected_results
    query = '{parentModels (last: 2){id, name}}'
    results = graphql(schema, query)
    expected_results = {
        'parentModels': [
            {'name': 'Cotu', 'id': test_parent_3.id}, {'name': 'Carolina', 'id': test_parent_2.id}
        ]
    }
    assert results.data == expected_results
    query = '{parentModels (first: 2){id, name}}'
    results = graphql(schema, query)
    expected_results = {
        'parentModels': [
            {'name': 'Adriel', 'id': test_parent_1.id}, {'name': 'Carolina', 'id': test_parent_2.id}
        ]
    }
    assert results.data == expected_results
    query = '{parentModels (order: ["id"]){id, name}}'
    results = graphql(schema, query)
    expected_results = {
        'parentModels': [
            {'name': 'Adriel', 'id': test_parent_1.id},
            {'name': 'Carolina', 'id': test_parent_2.id},
            {'name': 'Cotu', 'id': test_parent_3.id}
        ]
    }
    assert results.data == expected_results
    session.delete(test_parent_3)
    session.delete(test_parent_2)
    session.delete(test_parent_1)
    session.commit()


def test_like_query():
    test_parent_1 = ParentModel(name="Adriel")
    test_parent_2 = ParentModel(name="Carolina")
    test_parent_3 = ParentModel(name="Cotu")
    session.add(test_parent_1)
    session.add(test_parent_2)
    session.add(test_parent_3)
    session.commit()
    schema = R.Schema(R.Query)
    query = '{parentModel (like: {name: "Carolina"}) {id, name}}'
    results = graphql(schema, query)
    assert results.data == {"parentModel": {"id": test_parent_2.id, "name": "Carolina"}}
    session.delete(test_parent_3)
    session.delete(test_parent_2)
    session.delete(test_parent_1)
    session.commit()
