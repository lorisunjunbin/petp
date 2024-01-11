import de.hybris.platform.servicelayer.search.FlexibleSearchQuery
import groovy.json.JsonOutput

def checks = [
	[
		name :"Product Catalog Check",
	 	query:"SELECT {id} FROM {Catalog}",
	 	//regexFilter:""
	 	regexFilter:"(apparel|powertools|electronics)ProductCatalog"
	],
	[
		name :"Content Catalog Check",
	 	query:"SELECT {id} FROM {Catalog}",
	 	//regexFilter:""
	 	regexFilter:"(apparel|powertools|electronics)(-.*)?ContentCatalog"
	],
	[
		name :"Classification Catalog Check",
	 	query:"SELECT {id} FROM {Catalog}",
	 	//regexFilter:""
	 	regexFilter:"((P|p)owertools|(E|e)lectronics)Classification"
	],
	[
		name :"Website Check",
	 	query:"SELECT {uid} FROM {BaseSite}",
	 	//regexFilter:""
	 	regexFilter:"(apparel(-.*)?)|powertools|electronics"
	],
		[
		name :"BaseStore Check",
	 	query:"SELECT {uid} FROM {BaseStore}",
	 	//regexFilter:""
	 	regexFilter:"(apparel(-.*)?)|powertools|electronics"
	]
]

def sampleDataResults = []
checks.each { check -> 
	sampleDataResults << performCheck(check)
}
JsonOutput.prettyPrint(JsonOutput.toJson(sampleDataResults))

def performCheck(check) {

	def query = new FlexibleSearchQuery(check.query)
	query.setResultClassList([String.class])
	def result = flexibleSearchService.search(query)

	results = []
	result.result.each { row -> 

		def sampleDataFound = true;
		if (check.regexFilter!=null && !check.regexFilter.isEmpty()) {
			sampleDataFound = (row ==~ check.regexFilter)
		}

		if (sampleDataFound) {
			results << row;
		}
	}
	return [ checkName: check.name, checkQuery: check.query, regexFilter: check.regexFilter, checkResults: results ]
}