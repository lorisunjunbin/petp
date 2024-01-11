import de.hybris.platform.servicelayer.search.FlexibleSearchQuery
import groovy.json.JsonOutput

def query = new FlexibleSearchQuery('SELECT {passwordEncoding}, COUNT(0) FROM {User} GROUP BY {passwordEncoding}')
query.setResultClassList([String.class, Long.class])

def result = flexibleSearchService.search(query)

results = []

result.result.each { r -> 
  results << [ encoding: r[0], count: r[1] ]
}


JsonOutput.prettyPrint(JsonOutput.toJson(results))