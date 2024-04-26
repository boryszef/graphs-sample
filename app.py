from ariadne import QueryType, gql, make_executable_schema, ObjectType
from ariadne.asgi import GraphQL
from loguru import logger
from SPARQLWrapper import SPARQLWrapper, JSON


sparql = SPARQLWrapper(
    "https://dbpedia.org/sparql"
)
sparql.setReturnFormat(JSON)


type_defs = gql("""
    type Query {
        animals(taxon: String!): [Animal]
    }
    
    type Animal {
        label: String!
        abstract: String!
    }
""")


query = QueryType()


@query.field("animals")
def resolve_animal(*_, taxon=None):
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
    # logger.debug("Query: {}", query)
    sparql.setQuery(query)
    ret = sparql.queryAndConvert()
    # logger.debug("Response: {}", ret)
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


animal = ObjectType("Animal")

@animal.field("abstract")
def resolve_abstract(obj, *_):
    return obj['abstract']

@animal.field("label")
def resolve_abstract(obj, *_):
    return obj['label']


schema = make_executable_schema(type_defs, query, animal)
app = GraphQL(schema, debug=True)
