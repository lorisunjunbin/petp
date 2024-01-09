import groovy.json.JsonOutput
import org.apache.commons.configuration.Configuration

def config = configurationService.getConfiguration()
def auditingEnabled = config.getProperty('auditing.enabled')

def result = ['auditingEnabled': auditingEnabled]
JsonOutput.prettyPrint(JsonOutput.toJson(result))