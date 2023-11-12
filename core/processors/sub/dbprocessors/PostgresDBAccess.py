import logging

from core.processors.sub.dbprocessors.BaseDBAccess import BaseDBAccess

import psycopg

'''
 pip install psycopg
 
 OR refer to:   
 https://www.psycopg.org/psycopg3/docs/basic/install.html
 https://www.psycopg.org/psycopg3/docs/api/connections.html#the-connection-class
 https://www.postgresql.org/docs/current/libpq-connect.html#LIBPQ-PARAMKEYWORDS
 https://www.psycopg.org/psycopg3/docs/basic/params.html#query-parameters
 
 > .\psql.exe -d postgres -U postgres
 > \l
 > \c lorisunjunbin
 > \dt
 > \d+ userstore


create database lorisunjunbin;
create table userstore (id serial primary key, name varchar(100));

'''


class PostgresDBAccess(BaseDBAccess):
    cnx: psycopg.Connection

    def connect(self, host, port, database, user, pwd):
        config = {
            'host': host,
            'port': port,
            'dbname': database,
            'user': user,
            'password': pwd
        }
        self.cnx = psycopg.connect(**config)

    def execute(self, sql, param):
        if not hasattr(self, 'cnx'):
            logging.error("Postgres database is not connected, can NOT run sql: " + sql)
            return

        cur = None
        dataset = []
        try:

            if param is not None and len(param) > 0:
                cur = self.cnx.execute(sql, param)
            else:
                cur = self.cnx.execute(sql)

            for data in cur:
                dataset.append(data)

        except BaseException:
            self.cnx.rollback()

        finally:
            if self.require_commit(sql):
                self.cnx.commit()
                logging.debug(f" {cur.rowcount} affected. - {sql}")
            cur.close()

        return dataset

    def disconnect(self):

        if (hasattr(self, 'cnx')
                and self.cnx is not None
                and not self.cnx.closed):
            self.cnx.close()
