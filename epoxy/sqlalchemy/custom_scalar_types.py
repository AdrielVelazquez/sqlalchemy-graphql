import datetime

from graphql.core.language import ast
from graphql.core.type import GraphQLScalarType

__all__ = ["DateTimeType", "DictionaryType", "CamelCaseStringType", "to_delimiter_case"]


class DateTimeType(object):

    @staticmethod
    def serialize(dt):
        '''
        :param dt: datetime object
        :type dt: datetime
        :return: returns datetime in isoformat
        '''
        assert isinstance(dt, datetime.datetime)
        return dt.isoformat()

    @staticmethod
    def parse_literal(node):
        '''
        :param node: GraphQL Epoxy Query node
        :return: Conditional Return if node value is a string and converts to datetime object
        '''
        if isinstance(node, ast.StringValue):
            return datetime.datetime.strptime(node.value, "%Y-%m-%dT%H:%M:%S.%f")

    @staticmethod
    def parse_value(value):
        '''
        :param value: datetime string
        :return: datetime object
        '''
        return datetime.datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%f")


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


DateTimeType = GraphQLScalarType(name='DateTime', serialize=DateTimeType.serialize,
                                 parse_literal=DateTimeType.parse_literal,
                                 parse_value=DateTimeType.parse_value)

CamelCaseStringType = GraphQLScalarType(name='CamelCaseString', serialize=CamelCaseString.serialize,
                                 parse_literal=CamelCaseString.parse_literal,
                                 parse_value=CamelCaseString.parse_value)

DictionaryType = GraphQLScalarType(name='DictionaryType', serialize=DictionaryType.serialize,
                                   parse_literal=DictionaryType.parse_literal,
                                   parse_value=DictionaryType.parse_value)
