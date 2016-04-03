from graphql.core.language import ast
from graphql.core.type import GraphQLScalarType

__all__ = ["DictionaryType", "CamelCaseStringType", "to_delimiter_case"]


def to_delimiter_case(arg_str, delimiter="_"):
    delimiter_list = []
    for c in arg_str:
        if c.upper() == c and not c.isdigit():
            delimiter_list.append(delimiter)
        delimiter_list.append(c.lower())
    return "".join(delimiter_list)


class CamelCaseString(object):

    @staticmethod
    def serialize(value):
        return to_delimiter_case(value)

    @staticmethod
    def parse_literal(node):
        '''
        :param node: GraphQL Epoxy Query node
        :return: Conditional Return if node value is a string and converts to datetime object
        '''
        return to_delimiter_case(node.value)

    @staticmethod
    def parse_value(value):
        '''
        :param value: datetime string
        :return: datetime object
        '''
        return to_delimiter_case(value)


class DictionaryType(object):

    @staticmethod
    def serialize(value):
        return value

    @staticmethod
    def parse_literal(node):
        if isinstance(node, ast.ObjectValue):
            pairs = {}
            for pair in node.fields:
                key = to_delimiter_case(pair.name.value)
                pairs[key] = pair.value.value
            return pairs
        return node.value

    @staticmethod
    def parse_value(value):
        return value

CamelCaseStringType = GraphQLScalarType(name='CamelCaseString', serialize=CamelCaseString.serialize,
                                 parse_literal=CamelCaseString.parse_literal,
                                 parse_value=CamelCaseString.parse_value)

DictionaryType = GraphQLScalarType(name='DictionaryType', serialize=DictionaryType.serialize,
                                   parse_literal=DictionaryType.parse_literal,
                                   parse_value=DictionaryType.parse_value)
