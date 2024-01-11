import de.hybris.platform.core.*
import org.apache.commons.lang.*
import groovy.json.JsonOutput
  
def con = Registry.currentTenant.dataSource.connection
def result = [ header: [], data: [] ]
def sql = """
SELECT TOP 10
    t.NAME AS TableName,
    s.Name AS SchemaName,
    p.rows,
    SUM(a.total_pages) * 8 AS TotalSpaceKB,
    CAST(ROUND(((SUM(a.total_pages) * 8) / 1024.00), 2) AS NUMERIC(36, 2)) AS TotalSpaceMB,
    SUM(a.used_pages) * 8 AS UsedSpaceKB,
    CAST(ROUND(((SUM(a.used_pages) * 8) / 1024.00), 2) AS NUMERIC(36, 2)) AS UsedSpaceMB,
    (SUM(a.total_pages) - SUM(a.used_pages)) * 8 AS UnusedSpaceKB,
    CAST(ROUND(((SUM(a.total_pages) - SUM(a.used_pages)) * 8) / 1024.00, 2) AS NUMERIC(36, 2)) AS UnusedSpaceMB
FROM
    sys.tables t
INNER JOIN     
    sys.indexes i ON t.OBJECT_ID = i.object_id
INNER JOIN
    sys.partitions p ON i.object_id = p.OBJECT_ID AND i.index_id = p.index_id
INNER JOIN
    sys.allocation_units a ON p.partition_id = a.container_id
LEFT OUTER JOIN
    sys.schemas s ON t.schema_id = s.schema_id
WHERE
    t.NAME NOT LIKE 'dt%'
    AND t.is_ms_shipped = 0
    AND i.OBJECT_ID > 255
	AND s.name = 'dbo'
GROUP BY
    t.Name, s.Name, p.Rows
ORDER BY
    TotalSpaceMB DESC, t.Name
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