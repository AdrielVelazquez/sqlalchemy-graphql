from setuptools import setup, find_packages

setup(
    name="sqlalchemy_graphql",
    version="1.3",
    description="GraphQL extension for dealing with SQLAlchemy",
    long_description=open("README.rst", "r").read(),
    author="Adriel Velazquez",
    author_email="adrielvelazquez@gmail.com",
    packages=find_packages(exclude=['tests']),
    zip_safe=False,
    install_requires=[
        "sqlalchemy > 0.9",
        "graphql-epoxy"
    ],
    tests_require=['tox'],
)
