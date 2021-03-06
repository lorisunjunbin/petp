import logging

from pyhdbcli import Connection

from core.processors.sub.dbprocessors.BaseDBAccess import BaseDBAccess

from hdbcli import dbapi

'''
pip install hdbcli
 
refer to: 
https://pypi.org/project/hdbcli/
https://help.sap.com/docs/SAP_HANA_CLIENT/f1b440ded6144a54ada97ff95dac7adf/39eca89d94ca464ca52385ad50fc7dea.html?locale=en-US
'''


class HanaDBAccess(BaseDBAccess):
    cnx: Connection

    def connect(self, host, port, database, user, pwd):
        try:
            self.cnx =dbapi.connect(address = host, port = port, user = user, password = pwd)
        finally:
            logging.info("Hana database connected.")

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

            logging.info("Mysql execute successfully.")
        finally:
            self.cnx.commit()
            cur.close()

        return dataset

    def disconnect(self):
        if self.cnx is not None and self.cnx.is_connected():
            self.cnx.close()
