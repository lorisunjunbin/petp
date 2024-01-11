import de.hybris.platform.servicelayer.search.FlexibleSearchQuery
import groovy.json.JsonOutput

def prefixq = """
SELECT DISTINCT {c.extensionname}
FROM {ComposedType AS c}
WHERE {c.extensionname} NOT like 'core' AND {c.extensionname} like '%core'
"""

def query = new FlexibleSearchQuery(prefixq)

query.setResultClassList([String.class])

def result = flexibleSearchService.search(query)

def extensionpatterns = []

result.result.each { r ->
	def custom = r.split("core")[0]
	extensionpatterns << "{c.extensionname} like '${custom}%'"
	
}

def q = """
SELECT {c.code}, {s.code}, {c.extensionname}, count({a.pk}) AS attributes
FROM {ComposedType AS c
	JOIN ComposedType AS s ON {c.superType} = {s.PK}
	LEFT JOIN AttributeDescriptor AS a ON ({c.PK:o} = {a.enclosingType} AND {c.extensionname} = {a.extensionname} )
}
WHERE (
""" << extensionpatterns.join(" OR ") << """  ) 
	AND {s.code} NOT LIKE 'EnumerationValue'
	AND {s.code} NOT LIKE 'Item'
	AND {s.code} NOT LIKE 'Link'
GROUP BY {c.code}, {s.code}, {c.extensionname}
ORDER BY attributes
"""

println q

query = new FlexibleSearchQuery(q.toString())

query.setResultClassList([String.class, String.class, String.class, Integer.class])

result = flexibleSearchService.search(query)

results = []

result.result.each { r ->
  results << [ code: r[0], supertype: r[1], extension: r[2], attributes: r[3] ]
}

JsonOutput.prettyPrint(JsonOutput.toJson(results))