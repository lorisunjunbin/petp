import logging


class BaseDBAccess(object):

    def connect(self, host, port, database, user, pwd):
        logging.error("BaseDBAccess.connect is not implement yet!")

    def disconnect(self):
        logging.error("BaseDBAccess.disconnect is not implement yet!")

    def execute(self, sql, param):
        logging.error("BaseDBAccess.execute is not implement yet!")

    def require_commit(self, sql):
        if len(sql) == 0:
            return False

        first_letter_lowercase = sql[0].lower()

        if (first_letter_lowercase == 'i'
                or first_letter_lowercase == 'u'
                or first_letter_lowercase == 'd'):
            return True
        else:
            return False

    @staticmethod
    def get_dbaccess_by_type(prefix: str):
        class_name = prefix + 'DBAccess'
        module_name = 'core.processors.sub.dbprocessors.' + class_name
        module = __import__(module_name, fromlist=[module_name])
        dbAccess: BaseDBAccess = getattr(module, class_name)()
        return dbAccess
