from flask import Flask
from flask_graphql import GraphQLView
from graphene import List, ObjectType, Schema, String
from loguru import logger
from SPARQLWrapper import JSON, SPARQLWrapper


sparql = SPARQLWrapper(
    "https://dbpedia.org/sparql"
)
sparql.setReturnFormat(JSON)


class Animal(ObjectType):
    label = String()
    abstract = String()

    def resolve_label(root, info):
        return root['label']

    def resolve_abstract(root, info):
        return root['abstract']


class Query(ObjectType):
    animals = List(Animal, taxon=String(required=True))

    def resolve_animals(root, info, taxon):
        logger.debug("Executing query for {}, root/info = {}/{}", taxon, root, info)
        if taxon is None:
            return []
        query = (
            'select ?label ?abstract where {'
            '?name dbo:abstract ?abstract .'
            '?name rdfs:label ?label .'
            f'?name dbo:class / dbp:taxon "{taxon}"@en .'
            'FILTER ( LANG ( ?abstract ) = "en" ) .'
            'FILTER ( LANG ( ?label ) = "en" )'
            '} limit 20'
        )
        sparql.setQuery(query)
        ret = sparql.queryAndConvert()
        logger.debug("Response from DBpedia: {!r:60.60}(...)", ret)
        animals = ret["results"]["bindings"]
        if not animals:
            return []
        return [
            {
                "label": a['label']['value'],
                "abstract": a['abstract']['value']
            }
            for a in animals
        ]


schema = Schema(query=Query)


def create_app():
    app = Flask(__name__)
    app.add_url_rule(
        '/graphql',
        view_func=GraphQLView.as_view(
            'graphql',
            schema=schema,
            graphiql=True # for having the GraphiQL interface
        )
    )
    return app
