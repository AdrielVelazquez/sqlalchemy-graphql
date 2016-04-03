class QueryArgs(object):

    QUERY_ARGS = {
        "first": None,  # R.Int
        "last": None,  # R.Int
        "before": None,  # R.String
        "after": None,  # R.String
        "order": None,  # R.CamelCaseString.List
        "group": None,  # R.CamelCaseString.List
        "like": None,  # R.DictionaryType
        "match": None,  # R.DictionaryType
    }
