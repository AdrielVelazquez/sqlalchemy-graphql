from sqlalchemy.util._collections import AbstractKeyedTuple

__all__ = ["load_scalar_type"]


def add_query_args(args, query_args):
    args.update(query_args)
    return args


def load_scalar_type(registry):
    '''
    Load all custom Scalar types on the TypeRegistry.

    :param R: TypeRegistry for the SQLAlchemy Models
    '''
    from sqlalchemy_graphql.epoxy.custom_scalar_types import DictionaryType, CamelCaseStringType
    registry(DictionaryType)
    registry(CamelCaseStringType)


def flatten_keyed_tuple(keyed_tuple, model):
    flat_result = getattr(keyed_tuple, model.__name__)
    other_attrs = list(keyed_tuple._real_fields)
    other_attrs.remove(model.__name__)
    for attr in other_attrs:
        setattr(flat_result, attr, getattr(keyed_tuple, attr))
    return flat_result


def resolve_keyed_tuples(func):
    from functools import wraps

    @wraps(func)
    def func_wrapper(obj, args, info, model, single=False, query=None, additional_filters=None):
        results = func(obj, args, info, model, query, additional_filters, single)
        if isinstance(results, list):
            new_results = []
            for result in results:
                if isinstance(result, AbstractKeyedTuple):
                    flat_result = flatten_keyed_tuple(result, model)
                    new_results.append(flat_result)
                else:
                    new_results.append(result)
            return new_results
        elif isinstance(results, AbstractKeyedTuple):
            return flatten_keyed_tuple(results, model)
        return results
    return func_wrapper
