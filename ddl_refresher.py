from datetime import datetime
from getpass import getuser
from config import *
from queries_processor import QueriesProcessor


class DDLRefresher:

    def __init__(self):
        self.now = datetime.now().strftime("%Y-%m-%d")
        self.__qp = QueriesProcessor()
        self.__rep_path = BASE_PATH
        self.__install_tasks_path = os.path.join(self.__rep_path, 'install_tasks')

    def get_comment(self):
        """
        Получение стандартного комментария
        :return: Комментарий
        """
        return f'-- {getuser()} {self.now}\n'

    def get_ddl(self, db_name, object_name):
        """
        Возвращает собранную DDL объекта БД
        :param db_name: имя БД
        :param object_name: имя объекта
        :return:
        """
        comment = self.get_comment()
        block = self.__qp.get_ddl(db_name, object_name)
        return comment + f'USE {db_name} GO;\n' + block

    def get_ddl_path(self, db_name, object_type, object_name):
        """
        Возвращает путь к файлу объекта
        :param db_name: имя БД
        :param object_type: тип объекта
        :param object_name: имя объекта
        :return: путь к файлу объекта
        """
        return os.path.join(self.__rep_path, 'source', db_name, object_type, object_name)

    def refresh_ddls(self):
        """
        Обход перечисленных таблиц и запись их DDL
        """
        for db_name in DATABASES:
            for table_name in self.__qp.get_modify_tables(db_name):
                objname = table_name['table_name']
                filename = objname + '.sql'
                file_path = self.get_ddl_path(db_name, 'tables', filename)
                ddl = self.__qp.get_ddl(db_name, objname)
                if os.path.exists(file_path):
                    with open(file_path, 'w', encoding="utf_8") as wf:
                        wf.write(''.join(ddl) + '\n')
                else:
                    print(file_path)

    def run(self):
        """
        Запуск процесса обновления DDL
        """
        self.refresh_ddls()
