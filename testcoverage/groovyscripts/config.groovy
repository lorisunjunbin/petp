import de.hybris.platform.servicelayer.config.ConfigurationService
import java.lang.String
import java.lang.System
import groovy.json.JsonOutput
 
String[] array = "addonfilter.active cache.concurrency.level cache.persistenceproxy catalog.sync.workers catalog.sync.workers.cache cluster.broadcast.method.cluster.port cluster.broadcast.method.udp.interface cluster.broadcast.method.udp.multicastaddress cluster.broadcast.method.udp.port cluster.broadcast.methods cluster.interface cluster.node.groups cluster.maxid cronjob.maxthreads cronjob.timertask.loadonstartup default.session.cart.type db.pool.maxActive db.pool.maxIdle default.session.timeout hmc.caseinsensitivestringsearch hmc.default.autologin hmc.default.login hmc.default.password hmc.developermode hmc.storing.modifiedvalues.size hybris.improvedsessionhandling impex.import.workers installed.tenants session.replication.support session.timeout.checkinterval storefront.btg.enabled storefront.resourceBundle.cacheSeconds storefront.staticResourceFilter.response.header.Cache-Control storefront.show.debug.info system.unlocking.disabled task.excluded.cluster.ids task.processing.enabled task.workers.idle task.workers.max tenant.restart.on.connection.error tomcat.acceptcount tomcat.ajp.maxthreads tomcat.ajp.secureport tomcat.ajps.maxthreads tomcat.development.mode tomcat.generaloptions tomcat.javaoptions tomcat.legacy.deployment tomcat.maxidletime tomcat.maxthreads tomcat.minsparethreads".split()

results = []

array.each { r ->
  results << [ key: r, value:  configurationService.getConfiguration().getProperty(r)]
}

JsonOutput.prettyPrint(JsonOutput.toJson(results))