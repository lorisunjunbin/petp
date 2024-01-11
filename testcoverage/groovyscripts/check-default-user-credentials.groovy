import de.hybris.platform.core.model.user.UserModel
import groovy.json.JsonOutput

class DefaultUserCredentials {
  final String userName
  final String password
  final boolean sampleUser

  DefaultUserCredentials(final String userName, final String password, final boolean sampleUser) {
    this.userName = userName
    this.password = password
    this.sampleUser = sampleUser
  }
}

def userNameList = new ArrayList<DefaultUserCredentials>()
userNameList.add(new DefaultUserCredentials('admin', 'nimda', false))
userNameList.add(new DefaultUserCredentials('analyticsmanager', '1234', true))
userNameList.add(new DefaultUserCredentials('anonymous', 'suomynona', false))
userNameList.add(new DefaultUserCredentials('BackofficeIntegrationAdministrator', '1234', true))
userNameList.add(new DefaultUserCredentials('BackofficeIntegrationAgent', '1234', true))
userNameList.add(new DefaultUserCredentials('BackofficeProductAdministrator', '12341234', true))
userNameList.add(new DefaultUserCredentials('BackofficeProductManager', '12341234', true))
userNameList.add(new DefaultUserCredentials('BackofficeWorkflowAdministrator', '12341234', true))
userNameList.add(new DefaultUserCredentials('BackofficeWorkflowUser', '12341234', true))
userNameList.add(new DefaultUserCredentials('cmseditor', '1234', true))
userNameList.add(new DefaultUserCredentials('cmsmanager', '1234', true))
userNameList.add(new DefaultUserCredentials('cmsmanager-apparel-de', '1234', true))
userNameList.add(new DefaultUserCredentials('cmsmanager-apparel-uk', '1234', true))
userNameList.add(new DefaultUserCredentials('cmsmanager-electronics', '1234', true))
userNameList.add(new DefaultUserCredentials('cmsmanager-powertools', '1234', true))
userNameList.add(new DefaultUserCredentials('cmspublisher', 'Qwertz1234', true))
userNameList.add(new DefaultUserCredentials('cmsreviewer', 'Qwertz1234', true))
userNameList.add(new DefaultUserCredentials('cmstranslator', 'Qwertz1234', true))
userNameList.add(new DefaultUserCredentials('cmstranslator-Annette', '1234', true))
userNameList.add(new DefaultUserCredentials('cmstranslator-Seb', '1234', true))
userNameList.add(new DefaultUserCredentials('csagent', '1234', true))
userNameList.add(new DefaultUserCredentials('cxmanager', '12341234', true))
userNameList.add(new DefaultUserCredentials('cxuser', '12341234', true))
userNameList.add(new DefaultUserCredentials('hac_editor', 'editor', false))
userNameList.add(new DefaultUserCredentials('hac_viewer', 'viewer', false))
userNameList.add(new DefaultUserCredentials('integration-admin', '1234', true))
userNameList.add(new DefaultUserCredentials('integrationmonitoringtestuser', '1234', true))
userNameList.add(new DefaultUserCredentials('integrationservicestandarduser', '1234', true))
userNameList.add(new DefaultUserCredentials('integrationservicetestuser', '1234', true))
userNameList.add(new DefaultUserCredentials('marketingmanager', '1234', true))
userNameList.add(new DefaultUserCredentials('men@hybris.com', '12341234', true))
userNameList.add(new DefaultUserCredentials('menover30@hybris.com', '12341234', true))
userNameList.add(new DefaultUserCredentials('menvipbronze@hybris.com', '12341234', true))
userNameList.add(new DefaultUserCredentials('menvipgold@hybris.com', '12341234', true))
userNameList.add(new DefaultUserCredentials('productmanager', '1234', true))
userNameList.add(new DefaultUserCredentials('salesrep1@test.com', '12341234', true))
userNameList.add(new DefaultUserCredentials('salesrep2@test.com', '12341234', true))
userNameList.add(new DefaultUserCredentials('salesrep3@test.com', '12341234', true))
userNameList.add(new DefaultUserCredentials('sapInboundB2BCustomerUser', '1234', true))
userNameList.add(new DefaultUserCredentials('sapInboundB2CCustomerUser', '1234', true))
userNameList.add(new DefaultUserCredentials('sapInboundClassificationUser', '1234', true))
userNameList.add(new DefaultUserCredentials('sapInboundOMMOrderUser', '1234', true))
userNameList.add(new DefaultUserCredentials('sapInboundOMSOrderUser', '1234', true))
userNameList.add(new DefaultUserCredentials('sapInboundPriceUser', '1234', true))
userNameList.add(new DefaultUserCredentials('sapInboundProductUser', '1234', true))
userNameList.add(new DefaultUserCredentials('sapInboundUser', '1234PASSwd', false))
userNameList.add(new DefaultUserCredentials('searchmanager', '12341234', true))
userNameList.add(new DefaultUserCredentials('searchmanager', '12341234', true))
userNameList.add(new DefaultUserCredentials('sellerapprover', '12341234', true))
userNameList.add(new DefaultUserCredentials('vipbronze@hybris.com', '12341234', true))
userNameList.add(new DefaultUserCredentials('vipgold@hybris.com', '12341234', true))
userNameList.add(new DefaultUserCredentials('vipsilver@hybris.com', '12341234', true))
userNameList.add(new DefaultUserCredentials('vjdbcReportsUser', '1234', true))
userNameList.add(new DefaultUserCredentials('WarehouseAdministrator', '1234', true))
userNameList.add(new DefaultUserCredentials('WarehouseAgent', '1234', true))
userNameList.add(new DefaultUserCredentials('WarehouseManager', '1234', true))
userNameList.add(new DefaultUserCredentials('wfl_marketing', 'Qwertz1234', true))
userNameList.add(new DefaultUserCredentials('wfl_marketing_DE', 'Qwertz1234', true))
userNameList.add(new DefaultUserCredentials('wfl_marketing_EN', 'Qwertz1234', true))
userNameList.add(new DefaultUserCredentials('wfl_marketing_ES', 'Qwertz1234', true))
userNameList.add(new DefaultUserCredentials('wfl_marketing_FR', 'Qwertz1234', true))
userNameList.add(new DefaultUserCredentials('wfl_marketing_GB', 'Qwertz1234', true))
userNameList.add(new DefaultUserCredentials('wfl_marketing_GSW', 'Qwertz1234', true))
userNameList.add(new DefaultUserCredentials('wfl_marketing_IT', 'Qwertz1234', true))
userNameList.add(new DefaultUserCredentials('wfl_marketing_SWE', 'Qwertz1234', true))
userNameList.add(new DefaultUserCredentials('wfl_productManagement', 'Qwertz1234', true))
userNameList.add(new DefaultUserCredentials('wfl_purchase', 'Qwertz1234', true))
userNameList.add(new DefaultUserCredentials('wfl_translator_DE', 'Qwertz1234', true))
userNameList.add(new DefaultUserCredentials('wfl_translator_EN', 'Qwertz1234', true))
userNameList.add(new DefaultUserCredentials('wfl_translator_ES', 'Qwertz1234', true))
userNameList.add(new DefaultUserCredentials('wfl_translator_FR', 'Qwertz1234', true))
userNameList.add(new DefaultUserCredentials('wfl_translator_GB', 'Qwertz1234', true))
userNameList.add(new DefaultUserCredentials('wfl_translator_GSW', 'Qwertz1234', true))
userNameList.add(new DefaultUserCredentials('wfl_translator_IT', 'Qwertz1234', true))
userNameList.add(new DefaultUserCredentials('wfl_translator_SWE', 'Qwertz1234', true))
userNameList.add(new DefaultUserCredentials('women@hybris.com', '12341234', true))
userNameList.add(new DefaultUserCredentials('womenvipgold@hybris.com', '12341234', true))
userNameList.add(new DefaultUserCredentials('womenvipsilver@hybris.com', '12341234', true))
userNameList.add(new DefaultUserCredentials('yacctestcsagent', '12341234', true))

def defaultPasswords = []
def sampleUsersLeftEnabled = []
def sampleUsersLeftDisabled = []

userNameList.each { credentials ->
  try {
    UserModel user = defaultAuthenticationService.checkCredentials(credentials.userName, credentials.password)
    defaultPasswords << credentials.userName
  }
  catch (de.hybris.platform.servicelayer.security.auth.InvalidCredentialsException ignored) {
    try {
      UserModel user = userService.getUserForUID(credentials.userName)
      if (credentials.sampleUser) {
        if (user.isLoginDisabled()) {
          sampleUsersLeftDisabled << credentials.userName
        } else {
          sampleUsersLeftEnabled << credentials.userName
        }
      }
    } catch (de.hybris.platform.servicelayer.exceptions.UnknownIdentifierException e) {}
  }
}

def results = [defaultPasswords: defaultPasswords, sampleUsersEnabled: sampleUsersLeftEnabled, sampleUsersDisabled: sampleUsersLeftDisabled]

JsonOutput.prettyPrint(JsonOutput.toJson(results))
