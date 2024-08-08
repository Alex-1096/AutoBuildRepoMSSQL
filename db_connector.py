import pymssql
from config import *


class DBConnector:

    def __init__(self):
        self.__con = None
        self.__create_connection()

    def __create_connection(self) -> None:
        """
        Создание коннекта к БД
        """
        try:
            self.__con = pymssql.connect(
                server=SRV,
                user=USR,
                password=PW,
                as_dict=True)
        except Exception:
            Exception('Не удалось установить соединение с БД')

    def get_cursor(self) -> pymssql.Cursor:
        """
        Возвращает объект курсора
        :return: Cursor
        """
        return self.__con.cursor()


