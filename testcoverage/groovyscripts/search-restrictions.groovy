import de.hybris.platform.servicelayer.search.FlexibleSearchQuery
import groovy.json.JsonOutput

def query = new FlexibleSearchQuery('SELECT {sr.code}, {sr.name:o}, {sr.active}, {ct.code} as restrictedType, {p.uid} as principal, {sr.query} ' + 
'FROM {SearchRestriction AS sr ' + 
'	JOIN Principal AS p ON {sr.principal} = {p.PK} ' + 
'   JOIN ComposedType AS ct on {sr.restrictedType} = {ct.PK}} ' +
'WHERE {sr.active} = 1')

query.setResultClassList([String.class, String.class, Boolean.class, String.class, String.class, String.class])

def result = flexibleSearchService.search(query)

results = []

result.result.each { r -> 
  results << [ code: r[0], name: r[1], active: r[2], restrictedType: r[3], principal: r[4], query: r[5] ]
}

JsonOutput.prettyPrint(JsonOutput.toJson(results))