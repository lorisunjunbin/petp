import logging

from importlib import import_module


class BaseDBAccess:

    def connect(self, host, port, database, user, pwd):
        logging.error("BaseDBAccess.connect is not implemented yet!")

    def disconnect(self):
        logging.error("BaseDBAccess.disconnect is not implemented yet!")

    def execute(self, sql, param):
        logging.error("BaseDBAccess.execute is not implemented yet!")

    def require_commit(self, sql):
        return sql and sql[0].lower() in ['i', 'u', 'd']

    @staticmethod
    def get_dbaccess_by_type(prefix):
        class_name = prefix + 'DBAccess'
        module = import_module('core.processors.sub.dbprocessors.' + class_name)
        dbAccess: BaseDBAccess = getattr(module, class_name)()
        return dbAccess
