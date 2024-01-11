import de.hybris.platform.core.*
import groovy.json.JsonOutput
  
def con = Registry.currentTenant.dataSource.connection
def result = [ header: [], data: [] ]
def sql = """
SELECT TOP 10 s.Name AS SchemaName, t.name AS TableName, SUM(p.rows) AS TotalRowCount
FROM sys.tables AS t JOIN sys.partitions AS p ON t.object_id = p.object_id
AND p.index_id IN ( 0, 1 ) LEFT OUTER JOIN sys.schemas s ON t.schema_id = s.schema_id
WHERE s.name = 'dbo' GROUP BY s.Name, t.name
order by TotalRowCount desc;
"""

try {
  def r = con.prepareStatement(sql).executeQuery()
  def md = r.metaData

  for (int i = 0; i < md.columnCount; ++i) {
    result['header'] << [name: md.getColumnName(i + 1), type: md.getColumnTypeName(i+1)]
  }

  while (r.next()) {
    def row = []
    
    for (int i = 0; i < md.columnCount; ++i) {
      def o = r.getObject(i + 1)
      	
      if (o != null) {
        row << o
      }
    }
                         
	result['data'] << row
  }
  
  r.close()
}
finally {
  con.close()
}

JsonOutput.prettyPrint(JsonOutput.toJson(result))