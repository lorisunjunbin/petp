import groovy.json.JsonOutput
import org.apache.commons.configuration.Configuration

def config = configurationService.getConfiguration()
println config
def auditingEnabled = config.getProperty('auditing.enabled')

auditedItems = []
if (auditingEnabled) {
    def auditKeys = config.getKeys('audit')
    auditKeys.each { key ->

      if (key.startsWith('audit.') && key.endsWith('.enabled')) {
        def itemName = (key =~ 'audit\\.(.*)\\.enabled')[0][1]      
        auditedItems << itemName
      }
    }
}

def result = ['auditingEnabled': auditingEnabled, auditedItems: auditedItems]
JsonOutput.prettyPrint(JsonOutput.toJson(result))