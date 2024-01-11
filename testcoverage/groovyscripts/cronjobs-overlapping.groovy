import java.util.concurrent.TimeUnit

import java.time.temporal.ChronoUnit
import java.time.ZoneId
import java.time.ZoneOffset
import java.time.LocalDateTime

import de.hybris.platform.core.PK
import de.hybris.platform.servicelayer.search.FlexibleSearchQuery
import de.hybris.platform.cronjob.model.CronJobModel
import de.hybris.platform.servicelayer.cronjob.CronJobHistoryService;

import org.quartz.CronExpression

import groovy.json.JsonOutput
import groovy.transform.Field

@Field final int MAX_EXECUTIONS = 500
@Field final int MAX_COUNTER_EXECUTIONS_CHECKS = 200
@Field final int MAX_DAYS = 30
@Field final int DEFAULT_CRONJOB_DURATION_SECS = 60
@Field final String POTENTIAL_PHRASE = " (potentially overlaps, but too many combinations to check)"


def query = new FlexibleSearchQuery('SELECT {c.pk}, {c.code}, {c.active}, {c.nodeID}, {c.nodeGroup}, {t.cronExpression} FROM {CronJob as c JOIN Trigger AS t ON {t.cronjob} = {c.PK}} WHERE {t.cronExpression} is not null')
query.setResultClassList([Long.class, String.class, Boolean.class, Integer.class, String.class, String.class])

def result = flexibleSearchService.search(query)

results = []

result.result.each { r -> 

  def cj = modelService.get(new PK(r[0]));
  def cronExpStr = r[5];
  def averageDuration = getCronJobAverageExecutionTime(cj);
  def cronExpression = new CronExpression (cronExpStr)
  def cronSummary = cronExpression.expressionSummary
  def executionList = getCronJobExecutions(cronExpression, averageDuration, LocalDateTime.now())

  results << [ pk: r[0], code: r[1], active: r[2], nodeID: r[3], nodeGroup: r[4], cronExpression: r[5], cronSummary: cronSummary, averageDuration: averageDuration, executions: executionList]
}

// scan for overlapping executions in each cronjob and their executions
results.each{ r ->
	def overlaps = checkForCronJobOverlaps(r.code, r.executions, results);
	// add the overlaps to the results.
	r.overlaps = overlaps
}

results.each { r ->
	// remove the executions as no longer needed and would just consume print/parse time
	r.remove('executions')
}

JsonOutput.prettyPrint(JsonOutput.toJson(results))



// We have to optimise the whole iteration a bit so that we do not run into an timeout. Therefor we are using "potential" markings.
def checkForCronJobOverlaps(currentCronJobCode, currentCronjobExecutions, allResults) {
	def overlaps = []
	def loopCount = 0;
	def currentHasToManyExecutions = false

	if (currentCronjobExecutions.size == MAX_EXECUTIONS) {
		currentHasToManyExecutions = true
	}

	for (execution in currentCronjobExecutions) {
		for (otherCronJobResult in allResults) {
			def otherCronJobCode = otherCronJobResult.code
			def otherHasToManyExecutions = false

			if (otherCronJobResult.executions.size == MAX_EXECUTIONS) {
				otherHasToManyExecutions = true
			}

			// skip checking executions against itself or already found overlaps
			if (!otherCronJobCode.equals(currentCronJobCode) && !(overlaps.contains(otherCronJobCode) || overlaps.contains(otherCronJobCode + POTENTIAL_PHRASE))) {
				//if either the current or the counterpart is having more then the limit executions it will most likely be a overlap!
				if (otherHasToManyExecutions || currentHasToManyExecutions) {
					overlaps << otherCronJobCode + POTENTIAL_PHRASE
				} else {
					//we still need to limit the combinations matrix as otherwise the script will take for ever
					def tooMany = false
					def value = otherCronJobResult.executions.find { current ->
						loopCount++
						// check for any intersections in the executions
						if (current.intersects(execution)) {
							return true
						}

						if (loopCount > MAX_COUNTER_EXECUTIONS_CHECKS) {
							tooMany = true
							return true
						}
					}

					if (value != null && !tooMany) {
						overlaps << otherCronJobCode
						continue
					}

					if (tooMany) {
						overlaps << otherCronJobCode + POTENTIAL_PHRASE
					}
				}
			}
		}
	}
	return overlaps
}

// given a cron expression, and average duration, and a start time
// compute the next X execution ranges for the cronjob up to a maximum of MAX EXECUTIONS or MAX_DAYS in the future
def getCronJobExecutions(CronExpression cron, long averageDuration, LocalDateTime startTime) {

	def executionList = []
    def lastEndTime = startTime;
    def loopCount = 0; 
    while (lastEndTime.isBefore(startTime.plus(MAX_DAYS, ChronoUnit.DAYS)) && loopCount < MAX_EXECUTIONS) {
    	loopCount++
      	def nextStartTime = getNextExecutionTime(cron, lastEndTime)
    	def nextEndTime = nextStartTime.plus(averageDuration, ChronoUnit.SECONDS)

    	def newRange = new DateTimeRange(nextStartTime, nextEndTime)
        executionList << newRange
    	lastEndTime = nextEndTime
    }
    return executionList;
}

// retrieve the Average execution time for the specified job.
// Assume a default of DEFAULT_CRONJOB_DURATION_SECS if no history for execution, or a duration of 0 is returned.
def getCronJobAverageExecutionTime(CronJobModel cronjob) {
   
  def durationInSeconds = cronJobHistoryService.getAverageExecutionTime(cronjob, TimeUnit.SECONDS);	
  if (durationInSeconds == null || durationInSeconds == 0) {
  	// set a default duration for those cronjobs with no history
  	durationInSeconds = DEFAULT_CRONJOB_DURATION_SECS;
  }
  return durationInSeconds;
}
  
def getNextExecutionTime(CronExpression cron, LocalDateTime startDateTime) {
  def startDate = toDate(startDateTime);
  return toDateTime(cron.getNextValidTimeAfter(startDate));
}

def toDate(LocalDateTime localDateTime) {
  return Date.from(localDateTime.atZone(ZoneId.systemDefault()).toInstant());
}

def toDateTime(Date date) {
  return LocalDateTime.ofInstant(date.toInstant(), ZoneId.systemDefault() )
}

class DateTimeRange {
	long start;
	long end;

	DateTimeRange(LocalDateTime start, LocalDateTime end) {
		this.start = start.toInstant(ZoneOffset.ofTotalSeconds(0)).toEpochMilli()
		this.end = end.toInstant(ZoneOffset.ofTotalSeconds(0)).toEpochMilli()
	}

	public boolean intersects(DateTimeRange otherRange) {
		return (this.start <= otherRange.end) && (this.end >= otherRange.start)
	}
}
