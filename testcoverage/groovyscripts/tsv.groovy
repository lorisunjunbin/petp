
import de.hybris.platform.servicelayer.search.FlexibleSearchQuery
import de.hybris.bootstrap.config.ConfigUtil
import de.hybris.platform.core.Registry
import groovy.util.XmlParser
import org.apache.commons.lang.StringUtils
import org.apache.commons.collections.CollectionUtils
import de.hybris.platform.core.enums.TypeOfCollectionEnum
import de.hybris.platform.util.typesystem.TypeSystemUtils
import groovy.json.JsonOutput

//check the type system definition in custom extensions according to:
// https://help.sap.com/viewer/129a68efcdaf43dc94243b57f9aba5ad/2105/en-US/8ecae959b9bd46b8b426fa8dbde5cac4.html

def customExtensions = []
def composedTypeExcluded = []
composedTypeExcluded.add('RelationMetaType')
composedTypeExcluded.add('EnumerationMetaType')

def typeService = spring.getBean('typeService')
def flexibleSearchService = spring.getBean('flexibleSearchService')
def configurationService = spring.getBean('configurationService')
def ruleViolations = []
def customTypes = []

GENERIC_ITEM_TYPE = 'GenericItem'
GENERIC_ITEM_TABLE = 'genericitems'
GENERIC_RELATION_TABLE = 'links'
RELATION_CARDINALITY_MANY = 'many'

ATTRIBUTE_DESCRIPTOR_TYPE = 'AttributeDescriptor'

//// GENERIC SERVICES
//search service
executeSearch = { query ->
    flexibleQuery = new FlexibleSearchQuery(query)
    return flexibleSearchService.search(flexibleQuery)
}

def getCustomExtensions() {
    extensions = ConfigUtil.getPlatformConfig(Registry.class).getExtensionInfosInBuildOrder()
    platformPath = ConfigUtil.getPlatformConfig(Registry.class).getPlatformHome().getPath()

    configDirectoryPath = platformPath.substring(0, platformPath.length() - 'platform'.length()) + 'custom'

    return extensions.stream()
        .filter { extension ->
            extension.getExtensionDirectory().getPath().startsWith(configDirectoryPath)
        }
        .collect()
}

//extension services
def getStandardExtensions() {
    extensions = ConfigUtil.getPlatformConfig(Registry.class).getExtensionInfosInBuildOrder()
    platformPath = ConfigUtil.getPlatformConfig(Registry.class).getPlatformHome().getPath()

    configDirectoryPath = platformPath.substring(0, platformPath.length() - 'platform'.length()) + 'custom'

    return extensions.stream()
        .filter { extension ->
            !extension.getExtensionDirectory().getPath().startsWith(configDirectoryPath)
        }
        .collect()
}

def getAllLoadedExtensions() {
    allextensions = []
    ConfigUtil.getPlatformConfig(Registry.class).getExtensionInfosInBuildOrder().each { extensionInfo ->
        allextensions.add(extensionInfo.name)
    }
    return allextensions
}

boolean isStandardExtension(extensionName) {
    return STANDARD_EXTENSION_LIST.collect { it.getName() }.contains(extensionName)
}
boolean isCustomExtension(extensionName) {
    return !isStandardExtension(extensionName)
}

//composedtype helpers
def getAllStandardComposedTypeTables() {
    query = "SELECT {pk} from {ComposedType} WHERE {extensionName} IN ('" + getStandardExtensions().join("','").concat("')")
    return executeSearch(query).result.collect { it.table }
}

ALL_STANDARD_TABLES = getAllStandardComposedTypeTables()

boolean isDeploymentTableRequiredForComposedType(composedType) {
    if (GENERIC_ITEM_TYPE.equals(composedType.superType.code) && !Boolean.valueOf(composedType.abstract)) {
        return true
    }
}
boolean isDeploymentTableNotRequiredForComposedType(composedType) {
    return !isDeploymentTableRequiredForComposedType(composedType) && !composedType.superType.abstract
}

Integer getDeploymentTableTypeCodeFromComposedType(composedType) {
    def typexml = new XmlParser().parseText(composedType.xmldefinition)
    typecode = null
    if (CollectionUtils.isNotEmpty(typexml?.children())) {
        typecode = typexml?.children()?.get(0)?.@typecode
    }

    return typecode == null ? null : Integer.valueOf(typecode)
}

boolean catalogAwareAttributeDeclaredInCustomExtension(attributeDescriptor) {
    return isCustomExtension(attributeDescriptor.declaringEnclosingType.extensionName)
}

// relation helpers
boolean isRelationManyToMany(relationType) {
    if (RELATION_CARDINALITY_MANY.equals(relationType.sourceTypeCardinality.code) && RELATION_CARDINALITY_MANY.equals(relationType.targetTypeCardinality.code)) {
        return true
    }
    return false
}

boolean isCardinalityMany(relationType, element) {
    if ('source'.equals(element)) {
        return RELATION_CARDINALITY_MANY.equals(relationType.sourceTypeCardinality.code)
    }

    if ('target'.equals(element)) {
        return RELATION_CARDINALITY_MANY.equals(relationType.targetTypeCardinality.code)
    }
}

boolean isRelationElementOrdered(relationType, element) {
    if ('source'.equals(element)) {
        return isAttributeNotEmpty(relationType.sourceAttribute) && relationType.sourceAttribute.ordered
    }

    if ('target'.equals(element)) {
        return isAttributeNotEmpty(relationType.targetAttribute) && relationType.targetAttribute.ordered
    }
}

boolean isFeatureTypeRelation(attributeType) {
    return attributeType.class.equals(de.hybris.platform.core.model.type.CollectionTypeModel.class)
}

boolean isListCollectionType(relationType, element) {
    attributeType = relationType.sourceAttribute.attributeType

    if ('source'.equals(element)) {
        return isFeatureTypeRelation(attributeType) && attributeType.typeOfCollection.equals(TypeOfCollectionEnum.LIST)
    }

    if ('target'.equals(element)) {
        return isFeatureTypeRelation(attributeType) && attributeType.typeOfCollection.equals(TypeOfCollectionEnum.LIST)
    }
}

//type system helpers
def getTypeSystem() {
    return TypeSystemUtils.loadViaClassLoader(getAllLoadedExtensions())
}

//report
def writeReportLine(extensionName, rule, priority, element, description) {
    ruleViolations << [
        extension: extensionName,
        rule: rule,
        priority: priority,
        element: element,
        description: description
    ]
}

def printTypeDetail = { itemType ->
    customTypes << [typeCode: itemType.code,
         supertype: itemType.superType.code,
         itemType: itemType.itemtype,
         extension: itemType.extensionName
    ]
}

//// START TSV RULES

//rule descriptions
BOOLEANFIELDCANNOTBEOPTIONAL = "Fields of type java.lang.Boolean must be mandatory (optional='false') or a default value defined"
CATALOGVERSIONATTRIBUTESHOULDBEMARKEDUNIQUEFORCATALOGAWARETYPES = 'CatalogVersion attribute should be marked unique for Catalog aware types'
CMPPERSISTANCETYPEISDEPRECATED = "Attributes should not have a persistence type of 'cmp'."
DEPLOYMENTTABLEMUSTEXISTFORITEMEXTENDINGGENERICITEM = 'A deployment table must be defined for all Items extending GenericItem'
DEPLOYMENTTABLEMUSTEXISTFORMANYTOMANYRELATION = 'A deployment table must be defined for all many-to-many relations'
DEPLOYMENTTYPECODEMUSTBEGREATERTHANTENTHOUSAND = 'Type codes between 1 and 10000 are reserved for hybris'
FIELDNAMEMUSTSTARTWITHLOWERCASELETTER = 'Item attribute names must start with a lowercase letter'
IMMUTABLEFIELDMUSTHAVEINITIALVALUE = "Immutable fields (where write='false') must have initial set to 'true' or a default value defined"
JALOCLASSISNOTALLOWEDWHENADDINGFIELDSTOEXISTINGCLASS = "The jaloclass attribute is not allowed when autocreate='false' and generate='false'"
JALOPERSISTANCETYPEISDEPRECATED = "Attributes should not have a persistence type of 'jalo': use 'dynamic' instead."
LISTSINRELATIONSHOULDBEAVOIDED = "Any side of a relation that has cardinality='many' should have collectiontype='set' unless absolutely necessary"
MANDATORYFIELDMUSTHAVEINITIALVALUE = "Mandatory fields (where optional='false') must either have initial set to 'true' or a default value defined"
NODATABASEINDEXESFORUNIQUEATTRIBUTESOFTYPE = 'No database indexes defined for unique attributes of type'
NODEPLOYMENTTABLESHOULDEXISTFORITEMIFNOTEXTENDINGGENERICITEM = 'A deployment table must not be defined for any Items extending any item other than GenericItem'
NOUNIQUEATTRIBUTESDEFINEDFORTYPE = 'No unique attributes defined for type'
ONE2MANYRELATIONWHERETHEONESIDEISCATALOGAWARETYPEANDTHEMANYSIDEISNOT = 'One 2 many relation where the one side is a Catalog aware type and the many side is not'
ORDERINGOFRELATIONSHOULDBEAVOIDED = "Any side of a relation that has cardinality='many' should not have ordered='true' unless absolutely necessary"
RELATIONSHIPATTRIBUTEMUSTNOTBENULL = 'Relationship attribute qualifiers must not be null'
RELATIONSHIPQUALIFIERNAMEMUSTSTARTWITHLOWERCASELETTER = 'Relationship qualifier names must start with a lowercase letter'
TYPENAMEMUSTNOTSTARTWITHGENERATED = 'Type Names (including EnumTypes and Relations) must not start with the string Generated'
TYPENAMEMUSTSTARTWITHUPPERCASELETTER = 'Type Names (including EnumTypes and Relations) must start with an uppercase letter'
UNIQUEATTRIBUTESDONTMATCHCATALOGUNIQUEATTRIBUTEKEY="UniqueAttributes don't match the catalog unique attribute key (uniqueKeyAttributeQualifier)"
USEOFUNOPTIMIZEDATTRIBUTESISNOTRECOMMENDED = 'Use of unoptimized attributes is not recommended'
//composed type
void checkDeploymentTableMustExistForItemExtendingGenericItem(composedType) {
    if (isDeploymentTableRequiredForComposedType(composedType) && composedType.table.equals(GENERIC_ITEM_TABLE)) {
        writeReportLine(composedType.extensionName, 'DeploymentTableMustExistForItemExtendingGenericItem', 'H', composedType.code, DEPLOYMENTTABLEMUSTEXISTFORITEMEXTENDINGGENERICITEM)
    }
}

void checkNoDeploymentTableShouldExistForItemIfNotExtendingGenericItem(composedType) {
    if (isDeploymentTableNotRequiredForComposedType(composedType) && !ALL_STANDARD_TABLES.contains(composedType.table)) {
        writeReportLine(composedType.extensionName, 'NoDeploymentTableShouldExistForItemIfNotExtendingGenericItem', 'H', composedType.code, NODEPLOYMENTTABLESHOULDEXISTFORITEMIFNOTEXTENDINGGENERICITEM)
    }
}

void checkDeploymentTypeCodeMustBeGreaterThanTenThousand(composedType) {
    typecode = getDeploymentTableTypeCodeFromComposedType(composedType)

    if (typecode != null && typecode.intValue() < 10000) {
        writeReportLine(composedType.extensionName, 'DeploymentTypeCodeMustBeGreaterThanTenThousand', 'H', composedType.code, DEPLOYMENTTYPECODEMUSTBEGREATERTHANTENTHOUSAND)
    }
}

void checkTypeNameMustStartWithUppercaseLetter(composedType) {
    if (Character.isLowerCase(composedType.code.charAt(0))) {
        writeReportLine(composedType.extensionName, 'TypeNameMustStartWithUppercaseLette', 'M', composedType.code, TYPENAMEMUSTSTARTWITHUPPERCASELETTER)
    }
}

void checkTypeNameMustNotStartWithGenerated(composedType) {
    if (composedType.code.startsWith('Generated')) {
        writeReportLine(composedType.extensionName, 'TypeNameMustNotStartWithGenerated', 'M', composedType.code, TYPENAMEMUSTNOTSTARTWITHGENERATED)
    }
}

void checkCatalogVersionAttributeShouldBeMarkedUniqueForCatalogAwareTypes(composedType) {
    if (composedType.catalogItemType) {
        if (!composedType?.catalogVersionAttribute?.unique) {
            writeReportLine(composedType.extensionName, 'CatalogVersionAttributeShouldBeMarkedUniqueForCatalogAwareTypes', 'M', composedType.code + '.' + composedType?.catalogVersionAttribute?.qualifier, CATALOGVERSIONATTRIBUTESHOULDBEMARKEDUNIQUEFORCATALOGAWARETYPES)
        }
    }
}

void checkUniqueAttributesDontMatchCatalogUniqueAttributeKey(composedType) {
    if (composedType.catalogItemType && catalogAwareAttributeDeclaredInCustomExtension(composedType?.catalogVersionAttribute)) {
        uniqueAttributes = composedType.declaredattributedescriptors.stream().filter { attributeDescriptor ->
            attributeDescriptor.unique
        }.collect()

        uniqueKeyAttributes = composedType.uniqueKeyAttributes
        if (uniqueAttributes.size() != uniqueKeyAttributes.size()) {
            writeReportLine(composedType.extensionName, 'UniqueAttributesDontMatchCatalogUniqueAttributeKey', 'M', composedType.code, UNIQUEATTRIBUTESDONTMATCHCATALOGUNIQUEATTRIBUTEKEY)
        }
    }
}
//composed type attributes
void checkMandatoryFieldMustHaveInitialValue(attributeDescriptor) {
    if (!attributeDescriptor.optional) {
        if (!Boolean.valueOf(attributeDescriptor.initial) || attributeDescriptor.defaultValue == null) {
            writeReportLine(attributeDescriptor.extensionName, 'MandatoryFieldMustHaveInitialValue', 'M', attributeDescriptor.enclosingType.code + '.' + attributeDescriptor.qualifier, MANDATORYFIELDMUSTHAVEINITIALVALUE)
        }
    }
}

void checkImmutableFieldMustHaveInitialValue(attributeDescriptor) {
    if (!attributeDescriptor.writable) {
        if (!Boolean.valueOf(attributeDescriptor.initial) || attributeDescriptor.defaultValue == null) {
            writeReportLine(attributeDescriptor.extensionName, 'ImmutableFieldMustHaveInitialValue', 'M', attributeDescriptor.enclosingType.code + '.' + attributeDescriptor.qualifier, IMMUTABLEFIELDMUSTHAVEINITIALVALUE)
        }
    }
}

void checkBooleanFieldCannotBeOptional(attributeDescriptor) {
    if ('java.lang.Boolean'.equals(attributeDescriptor.attributeType.code)) {
        if (attributeDescriptor.optional && attributeDescriptor.defaultValue == null) {
            writeReportLine(attributeDescriptor.extensionName, 'BooleanFieldCannotBeOptional', 'M', attributeDescriptor.enclosingType.code + '.' + attributeDescriptor.qualifier, BOOLEANFIELDCANNOTBEOPTIONAL)
        }
    }
}

void checkJaloPersistanceTypeIsDeprecated(attributeDescriptor) {
    if (ATTRIBUTE_DESCRIPTOR_TYPE.equals(attributeDescriptor.itemtype) && !attributeDescriptor.property.booleanValue() && StringUtils.isBlank(attributeDescriptor.attributeHandler)) {
        writeReportLine(attributeDescriptor.extensionName, 'JaloPersistanceTypeIsDeprecated', 'M', attributeDescriptor.enclosingType.code + '.' + attributeDescriptor.qualifier, JALOPERSISTANCETYPEISDEPRECATED)
    }
}

void checkFieldNameMustStartWithLowercaseLetter(attributeDescriptor) {
    if (Character.isUpperCase(attributeDescriptor.qualifier.charAt(0))) {
        writeReportLine(attributeDescriptor.extensionName, 'FieldNameMustStartWithLowercaseLetter', 'M', attributeDescriptor.enclosingType.code + '.' + attributeDescriptor.qualifier, FIELDNAMEMUSTSTARTWITHLOWERCASELETTER)
    }
}

// relation type
void checkDeploymentTableMustExistForManyToManyRelation(relationType) {
    if (isRelationManyToMany(relationType) && GENERIC_RELATION_TABLE.equals(relationType.table)) {
        writeReportLine(relationType.extensionName, 'DeploymentTableMustExistForManyToManyRelation', 'H', relationType.code, DEPLOYMENTTABLEMUSTEXISTFORMANYTOMANYRELATION)
    }
}

boolean isAttributeEmpty(attribute) {
    return null == attribute || StringUtils.isBlank(attribute.qualifier)
}

boolean isAttributeNotEmpty(attribute) {
    return !isAttributeEmpty(attribute)
}

void checkRelationshipQualifierNameMustStartWithLowercaseLetter(relationType) {
    if (isAttributeNotEmpty(relationType.sourceAttribute) && Character.isUpperCase(relationType.sourceAttribute.qualifier.charAt(0))) {
        writeReportLine(relationType.extensionName, 'RelationshipQualifierNameMustStartWithLowercaseLetter', 'M', relationType.code + '.' + relationType.sourceAttribute.qualifier, RELATIONSHIPQUALIFIERNAMEMUSTSTARTWITHLOWERCASELETTER)
    }
    if (isAttributeNotEmpty(relationType.targetAttribute) && Character.isUpperCase(relationType.targetAttribute.qualifier.charAt(0))) {
        writeReportLine(relationType.extensionName, 'RelationshipQualifierNameMustStartWithLowercaseLetter', 'M', relationType.code + '.' + relationType.targetAttribute.qualifier, RELATIONSHIPQUALIFIERNAMEMUSTSTARTWITHLOWERCASELETTER)
    }
}

void checRelationshipAttributeMustNotBeNull(relationType) {
    if (isAttributeEmpty(relationType.sourceAttribute)) {
        writeReportLine(relationType.extensionName, 'RelationshipAttributeMustNotBeNull', 'M', relationType.code + ' source attribute', RELATIONSHIPATTRIBUTEMUSTNOTBENULL)
    }
    if (isAttributeEmpty(relationType.targetAttribute)) {
        writeReportLine(relationType.extensionName, 'RelationshipAttributeMustNotBeNull', 'M', relationType.code + ' target attribute', RELATIONSHIPATTRIBUTEMUSTNOTBENULL)
    }
}

void checkOrderingOfRelationShouldBeAvoided(relationType) {
    if (isCardinalityMany(relationType, 'source') && isRelationElementOrdered(relationType, 'source')) {
        writeReportLine(relationType.extensionName, 'OrderingOfRelationShouldBeAvoided', 'M', relationType.code + '.' + relationType.sourceAttribute.qualifier, ORDERINGOFRELATIONSHOULDBEAVOIDED)
    }

    if (isCardinalityMany(relationType, 'target') && isRelationElementOrdered(relationType, 'target')) {
        writeReportLine(relationType.extensionName, 'OrderingOfRelationShouldBeAvoided', 'M', relationType.code + '.' + relationType.targetAttribute.qualifier, ORDERINGOFRELATIONSHOULDBEAVOIDED)
    }
}

void checkListsInRelationShouldBeAvoided(relationType) {
    if (isCardinalityMany(relationType, 'source') && isListCollectionType(relationType, 'source')) {
        writeReportLine(relationType.extensionName, 'ListsInRelationShouldBeAvoided', 'M', relationType.code + '.' + relationType.sourceAttribute.qualifier, LISTSINRELATIONSHOULDBEAVOIDED)
    }

    if (isCardinalityMany(relationType, 'target') && isListCollectionType(relationType, 'target')) {
        writeReportLine(relationType.extensionName, 'ListsInRelationShouldBeAvoided', 'M', relationType.code + '.' + relationType.targetAttribute.qualifier, LISTSINRELATIONSHOULDBEAVOIDED)
    }
}

//// checks
//check types
def checkComposedType = { composedType ->
    checkDeploymentTableMustExistForItemExtendingGenericItem(composedType)
    checkNoDeploymentTableShouldExistForItemIfNotExtendingGenericItem(composedType)
    checkDeploymentTypeCodeMustBeGreaterThanTenThousand(composedType)
    checkTypeNameMustStartWithUppercaseLetter(composedType)
    checkTypeNameMustNotStartWithGenerated(composedType)
    checkCatalogVersionAttributeShouldBeMarkedUniqueForCatalogAwareTypes(composedType)
    checkUniqueAttributesDontMatchCatalogUniqueAttributeKey(composedType)

    //check type attributes
    composedType.declaredattributedescriptors.each { attributeDescriptor ->
        checkMandatoryFieldMustHaveInitialValue(attributeDescriptor)
        checkImmutableFieldMustHaveInitialValue(attributeDescriptor)
        checkBooleanFieldCannotBeOptional(attributeDescriptor)
        checkJaloPersistanceTypeIsDeprecated(attributeDescriptor)
    }
}

//check relations
def checkRelationType = { relationType ->
    checkDeploymentTableMustExistForManyToManyRelation(relationType)
    checkRelationshipQualifierNameMustStartWithLowercaseLetter(relationType)
    checkOrderingOfRelationShouldBeAvoided(relationType)
    checkListsInRelationShouldBeAvoided(relationType)
    checRelationshipAttributeMustNotBeNull(relationType)
}

def checkComposedTypeDebug = { composedType ->
    composedType.declaredattributedescriptors.each { attributeDescriptor ->
        println attributeDescriptor.qualifier
        println getTypeSystem().getAttribute(composedType.code, attributeDescriptor.qualifier).getCustomProps()
        println getTypeSystem().getType(composedType.code).uniqueAttributes
        println ''
    }
}

//START MAIN EXECUTION

STANDARD_EXTENSION_LIST = getStandardExtensions()
customExtensions = getCustomExtensions()

//// QUERY DEFINITIONS
//TYPES
def queryComposedTypes = "SELECT {item:PK} from {ComposedType as item} WHERE {item:extensionName} IN ('" + customExtensions.join("','") + "') ORDER BY {item:code}"

//RELATIONS
def queryRelationTypes = "SELECT {PK} FROM {RelationMetaType!} WHERE {extensionName} IN ('" + customExtensions.join("','") + "')"

try {
    executeSearch(queryComposedTypes).result.each {
        checkComposedType(it)
    }
    executeSearch(queryRelationTypes).result.each { checkRelationType(it) }
    executeSearch(queryComposedTypes).result.each { printTypeDetail(it) }

    result = [violations: ruleViolations, customTypes: customTypes, extensions: customExtensions]
    
    return JsonOutput.prettyPrint(JsonOutput.toJson(result))
}catch (Exception ex) {
    ex.printStackTrace()
}
