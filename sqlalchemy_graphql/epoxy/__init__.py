from sqlalchemy_graphql.epoxy.utils import load_scalar_type


class EpoxySQLAlchemy(object):
    """Main class to access Interface and query args."""

    query_args = {
        "first": None,  # R.Int
        "last": None,  # R.Int
        "before": None,  # R.String
        "after": None,  # R.String
        "order": None,  # R.CamelCaseString.List
        "group": None,  # R.CamelCaseString.List
        "like": None,  # R.DictionaryType
        "match": None,  # R.DictionaryType
    }

    def register(self, registry):
        """Main function that returns the additional query args and Interface."""
        load_scalar_type(registry)
        self.query_args["first"] = registry.Int
        self.query_args["last"] = registry.Int
        self.query_args["before"] = registry.String
        self.query_args["after"] = registry.String
        self.query_args["order"] = registry.CamelCaseString.List
        self.query_args["group"] = registry.CamelCaseString.List
        self.query_args["like"] = registry.DictionaryType
        self.query_args["match"] = registry.DictionaryType

        class FuncBase(registry.Interface):
            func = registry.DictionaryType(args={"field": registry.CamelCaseString, "op": registry.String})
            count = registry.Int(args={"distinct": registry.CamelCaseString})

            def resolve_func(self, obj, args, info):
                if args.get("op") == "distinct":
                    return getattr(obj, args.get("field"))
                target = "{}_{}".format(args.get("field"), args.get("op"))
                return getattr(obj, target)

            def resolve_count(self, obj, args, info):
                target = "count"
                if args.get("distinct"):
                    target = "{}_{}_{}".format(args.get("distinct"), "distinct", "count")
                return getattr(obj, target)

        self.FuncBase = FuncBase
