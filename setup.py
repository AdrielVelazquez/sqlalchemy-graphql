from setuptools import setup

setup(
    name="sqlalchemy_sphinx",
    version="0.8.3",
    description="SQLAlchemy extension for dealing with SphinxQL",
    long_description=open("README.rst", "r").read(),
    author="SET by Conversant",
    author_email="adrielvelazquez@gmail.com",
    packages=['sqlalchemy_sphinx'],
    zip_safe=False,
    install_requires=[
        "sqlalchemy > 0.9",
    ],
    tests_require=['tox'],
    entry_points={
     'sqlalchemy.dialects': [
          'sphinx = sqlalchemy_sphinx.mysqldb:Dialect',
          'sphinx.cymysql = sqlalchemy_sphinx.cymysql:Dialect',
          'sphinx.mysqldb = sqlalchemy_sphinx.mysqldb:Dialect'
          ]
    }
)
