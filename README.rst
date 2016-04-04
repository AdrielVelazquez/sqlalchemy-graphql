SQLAlchemy GraphQL 
===================


SQLAlchemy GraphQL is a plugin for GraphQL Epoxy that provides universal functions for
SQLAlchemy models being used for GraphQL

**Graphene Support Coming Soon**

Installation
------------

SQLAlchemy Sphinx is available on pypi under the package name
``sqlalchemy-graphql``, you can get it by running:

.. code:: sh

    pip install sqlalchemy-graphql


Usage
-----

The first step is registering your type registry. This adds all the features into your
registry without you having to do any work. It leverages GraphQL aliasing. 

.. code:: python

    from epoxy import TypeRegistry

    from sqlalchemy_graphql.epoxy import EpoxySQLAlchemy

    R = TypeRegistry()
    esql = EpoxySQLAlchemy()
    esql.register(R)


Once this is done, your registry now has a new Interface called FuncBase, which will be the one of the 
interfaces all your graphql models will use.

Here we'll define the SQLAlchemy models using epoxy's Registry decorators.

.. code:: python

    from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
    from sqlalchemy.ext.declarative import declarative_base
    from sqlalchemy.orm import relationship, backref, sessionmaker

    from youe_application import R
    engine = create_engine('sqlite:///:memory:', echo=True)
    Base = declarative_base(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()


    @R.ParentModel.CanBe
    class ParentModel(Base):
        __tablename__ = "parents"
        id = Column(Integer, primary_key=True)
        name = Column(String)


    @R.ChildModel.CanBe
    class ChildModel(Base):
        __tablename__ = "children"
        id = Column(Integer, primary_key=True)
        name = Column(String)
        parent_id = Column(Integer, ForeignKey("parents.id"), nullable=False)
        parent = relationship("ParentModel", backref=backref("children", lazy="dynamic", cascade="all,delete-orphan"))



And finally defining the GraphQL models. 

The first things that need to be done is during any relational, or sqlalchemy model query, we need to
include the esql.quey_args. I created a global varaible below, but you can add them however you wish.


.. code:: python

    from your_application import R, esql
    from your_application.your_sqlalchemy_models import ChildModel as BaseChildModel, ParentModel as BaseParentModel, session

    from sqlalchemy_graphql.epoxy.utils import add_query_args
    from sqlalchemy_graphql.epoxy.query import resolve_sqlalchemy

    model_args = add_query_args({"id": R.Int, "name": R.String, "ids": R.Int.List}, esql.query_args)


    class ParentModel(R.Implements.FuncBase):
        id = R.Int
        name = R.String
        children = R.ChildModel.List(args=model_args)

        def resolve_children(self, obj, args, info):
            return resolve_sqlalchemy(obj, args, info, BaseChildModel, query=obj.children)


    class ChildModel(R.Implements.FuncBase):
        id = R.Int
        name = R.String
        parent = R.ParentModel(args=model_args)

        def resolve_parent(self, obj, args, info):
            return resolve_sqlalchemy(obj, args, info, BaseParentModel, query=obj.parent)


    class Query(R.ObjectType):
        parent_model = R.ParentModel(args=model_args)
        child_model = R.ChildModel(args=model_args)
        parent_models = R.ParentModel.List(args=model_args)
        child_models = R.ChildModel.List(args=model_args)

        def resolve_parent_model(self, obj, args, info):
            query = session.query(BaseParentModel)
            return resolve_sqlalchemy(obj, args, info, BaseParentModel, query=query, single=True)

        def resolve_child_model(self, obj, args, info):
            query = session.query(BaseChildModel)
            return resolve_sqlalchemy(obj, args, info, BaseChildModel, query=query, single=True)

        def resolve_parent_models(self, obj, args, info):
            query = session.query(BaseParentModel)
            return resolve_sqlalchemy(obj, args, info, BaseParentModel, query=query)

        def resolve_child_models(self, obj, args, info):
            query = session.query(BaseChildModel)
            return resolve_sqlalchemy(obj, args, info, BaseChildModel)
        )

You'll notice in the resolves for the Query, we're using the helper function resolve_sqlalchemy, proided by sqlalchemy-graphql to resolve any query arguements that are going to be used. 

All that needs to be passed in is a Base query that has the SQLAlchemy model as the first argument,
and you're good to go. 


Examples
--------


The tests provided has a ton of examples, 
but here is some basic queries you can now do with your universal func. 


You can essentially do anything that the SQLAlchemy func offers you to do

The basic formating is:

.. code:: python

    func(field:"{YOUR TARGET ATTRIBUTE}", op:"YOUR OPERATION")
    func(field:"id", op:"min")}
    func(field:"id", op:"max")}
    func(field:"count", op:"sum")}

.. code:: python

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


    query = '{parentModels {distinctName: count(distinct:"name")}}'
    results = graphql(schema, query)
    # results.data == {'parentModels': [{'distinctName': 2}]}


    query = '{parentModels (first: 1, after:"Adriel", order:["name"]){id, name}}'
    results = graphql(schema, query)

    '''results.data
    {
        'parentModels': [
            {'name': 'Carolina', 'id': test_parent_2.id}
        ]
    }
    '''