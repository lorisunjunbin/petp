import de.hybris.platform.servicelayer.search.FlexibleSearchQuery
import groovy.json.JsonOutput
import java.time.LocalDateTime
import java.time.Instant
import java.time.ZoneOffset


import groovy.transform.Field


@Field final int OLDER_THAN_DAYS = 14

def query = new FlexibleSearchQuery(
	'SELECT {c.code}, {c.active}, {c.startTime}, {c.endTime}, {e.code}, {t.cronExpression} ' + 
	'FROM {CronJob AS c ' + 
	'	LEFT OUTER JOIN Trigger AS t ON {t.cronjob} = {c.PK} ' + 
	'	JOIN EnumerationValue AS e ON {e.PK} = {c.status} } ' + 
	'WHERE ' + 
	'{c.active} = 1 AND ' + 
	'{t.cronExpression} IS NULL AND ' + 
	'{e.code} = \'FINISHED\' AND ' + 
	'{c.endTime} < ?cleanupDate')
def instant = LocalDateTime.now().minusDays(OLDER_THAN_DAYS).toInstant(ZoneOffset.UTC);
def cleanupDate = Date.from(instant);

query.addQueryParameter("cleanupDate", cleanupDate)

query.setResultClassList([String.class, Boolean.class, Date.class, Date.class, String.class, String.class])

query.setCount(100)

def result = flexibleSearchService.search(query)

results = []

result.result.each { r -> 
  results << [ cronjob: r[0], active: r[1], startTime: r[2], endTime: r[3], status: r[4], cronExpression: "" ]
}


JsonOutput.prettyPrint(JsonOutput.toJson(results))
