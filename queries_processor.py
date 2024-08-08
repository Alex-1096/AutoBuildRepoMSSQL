from db_connector import DBConnector
from queries import *


class QueriesProcessor:
    """
    Класс получения данных из БД
    """

    def __init__(self):
        self.__cur = DBConnector().get_cursor()

    def get_cur_ver(self):
        """
        Получение текущей версии БД
        """
        self.__cur.execute(get_cur_ver)
        res = str(self.__cur.fetchone().get('version_num'))
        return res

    def get_ddl(self, db_name, table_name):
        self.__cur.execute(get_ddl_query.format(db_name, table_name))
        res = '\n'.join(line.get('Item') for line in self.__cur.fetchall())
        return self.decode_string(res)

    def get_modify_tables(self, db_name):
        self.__cur.execute(get_modify_tables.format(db_name))
        return self.__cur.fetchall()

    def get_all_objects(self, db_name, obj_type):
        self.__cur.execute(get_all_objects.format(db_name, obj_type))
        return self.__cur.fetchall()

    def get_schemas(self, db_name):
        self.__cur.execute(get_schemas.format(db_name))
        return self.__cur.fetchall()

    def get_triggers(self, db_name):
        self.__cur.execute(get_triggers.format(db_name))
        return self.__cur.fetchall()

    def get_functions(self, db_name):
        self.__cur.execute(get_functions.format(db_name))
        return self.__cur.fetchall()

    @staticmethod
    def decode_string(text):
        """
        Декодирует строку из кодировки Latin1 в кодировку CP1251.
        :return: str: Декодированная строка в кодировке CP1251.
        """
        return text.encode('latin1').decode('cp1251')