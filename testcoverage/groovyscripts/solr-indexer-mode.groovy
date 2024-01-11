import de.hybris.platform.servicelayer.search.FlexibleSearchQuery
import groovy.json.JsonOutput

def query = new FlexibleSearchQuery('SELECT {fsc:name}, {ic:indexMode} FROM {SolrFacetSearchConfig AS fsc LEFT JOIN SolrIndexConfig AS ic ON {fsc:solrIndexConfig} = {ic:PK}}')
query.setResultClassList([String.class, de.hybris.platform.solrfacetsearch.enums.IndexMode.class])

def result = flexibleSearchService.search(query)

results = []

result.result.each { r -> 
  results << [ config: r[0], mode: r[1] ]
}


JsonOutput.prettyPrint(JsonOutput.toJson(results))