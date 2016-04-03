from sqlalchemy_graphql.epoxy.custom_scalar_types import DictionaryType


def test_dictionary_type_sanity():
    node = type("node", (), {"value": "Adriel"})
    returned = DictionaryType.parse_literal(node())
    assert returned == "Adriel"
