import logging

from mysql.connector import MySQLConnection

from core.processors.sub.dbprocessors.BaseDBAccess import BaseDBAccess

import mysql.connector
from mysql.connector import errorcode

'''
 pip install mysql-connector-python
 
 OR refer to:   https://dev.mysql.com/doc/index-connectors.html

'''


class MysqlDBAccess(BaseDBAccess):
    cnx: MySQLConnection

    def connect(self, host, port, database, user, pwd):
        try:
            config = {
                'host': host,
                'port': port,
                'database': database,
                'user': user,
                'password': pwd,
                'raise_on_warnings': True
            }
            self.cnx = mysql.connector.connect(**config)

        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                logging.error("Something is wrong with your user name or password")
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                logging.error("Database does not exist")
            else:
                logging.error(err.msg)
        else:
            logging.info("Mysql database connected.")

    def execute(self, sql, param):
        cur = self.cnx.cursor(dictionary=True)
        dataset = []
        try:

            if param is not None and len(param) > 0:
                cur.execute(sql, param)
            else:
                cur.execute(sql)

            for data in cur:
                dataset.append(data)

        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
                logging.error("already exists.")
            else:
                logging.error(err.msg)
        else:
            logging.info("Mysql execute successfully.")
        finally:
            self.cnx.commit()
            cur.close()

        return dataset

    def disconnect(self):
        if self.cnx is not None and self.cnx.is_connected():
            self.cnx.close()
