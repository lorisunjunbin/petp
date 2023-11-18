import logging


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
        module_name = 'core.processors.sub.dbprocessors.' + class_name
        module = __import__(module_name, fromlist=[module_name])
        return getattr(module, class_name)()
