import logging

from core.processor import Processor
from core.processors.sub.dbprocessors.BaseDBAccess import BaseDBAccess


class DB_ACCESSProcessor(Processor):

    TPL: str = '{"type":"Mysql|Hana|Postgres|Sqlite", "host":"192.168.8.8", "port":"3306", "database":"customdb", "user":"admin", "pwd":"nimda","sql":"select * from user where username=%s and id=%s","param":"admin, id","data_key":"dataset", "param_key":"sql_param"}'

    DESC: str = f'''
        Provide generic Database access capacity. Connects to a database, executes a SQL query,
        and stores the result set in the data_chain under the specified key.

        Requires python db connector/driver:
          Mysql    > pip install mysql-connector-python
          Hana     > pip install hdbcli
          Postgres > pip install psycopg
          Sqlite   > only "database" is required.

        - type: Database type, one of Mysql, Hana, Postgres, or Sqlite (supports expression, default: "Mysql|Hana|Postgres|Sqlite")
        - host: Database server hostname or IP address (supports expression, default: "192.168.8.8")
        - port: Database server port number (supports expression, default: "3306")
        - database: Name of the database to connect to (supports expression, default: "customdb")
        - user: Database user for authentication (supports expression, default: "admin")
        - pwd: Database password for authentication (supports expression, default: "nimda")
        - sql: SQL query to execute, supports parameterized placeholders like %s (supports expression, default: "select * from user where username=%s and id=%s")
        - param: Comma-separated parameter values for the parameterized SQL query (supports expression, default: "admin, id")
        - data_key: Key name in data_chain to store the query result set (supports expression, default: "dataset")
        - param_key: Key name in data_chain to retrieve SQL parameters from; takes precedence over "param" if provided (supports expression, default: "sql_param")

        {TPL}

    '''
    def get_category(self) -> str:
        return super().CATE_DATABASE

    def process(self):
        type = self.expression2str(self.get_param('type'))
        host = self.expression2str(self.get_param('host'))
        port = self.expression2str(self.get_param('port'))
        database = self.expression2str(self.get_param('database'))
        user = self.expression2str(self.get_param('user'))
        pwd = self.expression2str(self.get_param('pwd'))
        data_key = self.expression2str(self.get_param('data_key'))

        sql = self.expression2str(self.get_param('sql'))

        param_str = self.get_data(self.get_param('param_key')) if self.has_param('param_key') \
            else self.expression2str(self.get_param('param'))

        data_set = []
        dbAccess: BaseDBAccess = None
        try:
            dbAccess: BaseDBAccess = BaseDBAccess.get_dbaccess_by_type(type)
            dbAccess.connect(host, port, database, user, pwd)
            data_set = dbAccess.execute(sql, tuple(map(str, param_str.split(','))) if param_str is not None and len(param_str) >0 else '')
        finally:
            if dbAccess is not None:
                dbAccess.disconnect()

        logging.debug(f'The size of "{data_key}" after db access: {len(data_set) if data_set is not None else 0}')

        self.populate_data(data_key, data_set)
