# Get birds with abstracts

birds = """
  select ?name ?label ?abstract where {
    ?name dbo:abstract ?abstract .
    ?name rdfs:label ?label .
    ?name dbo:class / dbp:label "Bird"@en .
    FILTER ( LANG ( ?abstract ) = 'en' ) .
    FILTER ( LANG ( ?label ) = 'en' )
  } limit 10
"""

# Get mammals of Europe with abstracts

mammals_of_europe = """
  select ?label ?abstract where {
    ?name dcterms:subject dbc:Mammals_of_Europe .
    ?name dbo:abstract ?abstract .
    ?name rdfs:label ?label .
    FILTER ( LANG ( ?label ) = 'en' ) .
    FILTER ( LANG ( ?abstract ) = 'en' )
  } limit 10
"""

