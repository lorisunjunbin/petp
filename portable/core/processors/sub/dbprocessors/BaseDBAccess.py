import importlib
import logging
import os


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
        file_path = (os.path.realpath('core') + os.sep + 'processors'
                     + os.sep + 'sub' + os.sep + 'dbprocessors' + os.sep + prefix + 'DBAccess.py')
        class_name = prefix + 'DBAccess'
        spec = importlib.util.spec_from_file_location(class_name, file_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        dbAccess: BaseDBAccess = getattr(module, class_name)()
        return dbAccess
