from datetime import datetime
from queries_processor import QueriesProcessor
from config import BASE_PATH, DATABASES, OBJECT_TYPES, IGNORED_SCHEMAS
from getpass import getuser
import os
import re
import regex


class RebuildDDL:
    """Класс предназначен для обновления всех файлов репозитория"""

    def __init__(self):
        self.now = datetime.now().strftime("%Y-%m-%d")
        self.__qp = QueriesProcessor()
        self.__rep_path = BASE_PATH
        self.__db_list = DATABASES
        self.__obj_types = OBJECT_TYPES

    def get_comment(self):
        """
        Получение стандартного комментария
        :return: Комментарий
        """
        return f'-- {getuser()} {self.now}\n'

    def get_ddl(self, db_name, schema_name, object_name):
        """
        Возвращает собранную DDL объекта БД
        :param db_name: имя БД
        :param schema_name: наименование схемы
        :param object_name: имя объекта
        :return:
        """
        comment = self.get_comment()
        object_with_schema = f'{schema_name}.{object_name}'
        block = self.__qp.get_ddl(db_name, object_with_schema)
        block = self.cleanse_text(block)
        res = comment + f'USE {db_name}\nGO;\n' + block
        return res

    def get_arr_obj(self, db_name, obj_type):
        """
        Возвращает имена всех объектов указанного типа
        :param db_name: имя БД
        :param obj_type: тип объекта ('tables', 'procedures', 'views', 'triggers')
        :return:
        """
        result = self.__qp.get_all_objects(db_name, obj_type)
        return result

    @staticmethod
    def cleanse_text(content):
        """
        Форматирует ddl
        """
        content = re.sub(r'\n\s*\n', r'\n', content)
        content = re.sub(r'^\s*', '', content)
        content = content.split('\n')
        content = list(map(lambda row: row.expandtabs(tabsize=4).rstrip() + '\n', content))
        content = [row for row in content if 'SelectTopNRows' not in row]
        content = ''.join(content)
        content = re.sub(r'\n+', '\n', content)
        pattern = r'[\[\'](?:[^\[\]\']++|(?0))++[\]\'](*SKIP)(*F)| '
        content = regex.sub(pattern, ' ', content)
        return content

    @staticmethod
    def remove_folder(folder_path):
        """
        Функция remove_folder удаляет все файлы в указанной папке.
        Аргументы:
        :db_name: строка, имя базы данных
        :obj_type: строка, тип объекта
        """
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                os.unlink(file_path)

    def get_objects_path(self, db_name, schema_name, object_type) -> str:
        """
        Возвращает путь к папке с объектами
        :param db_name: имя БД
        :param schema_name: наименование схемы
        :param object_type: тип объекта
        :return: путь к папке с объектами
        """
        return str(os.path.join(self.__rep_path, 'source', db_name, schema_name, object_type))

    def get_ddl_path(self, db_name, schema_name, object_type, object_name):
        """
        Возвращает путь к файлу объекта
        :param db_name: имя БД
        :param schema_name: наименование схемы
        :param object_type: тип объекта
        :param object_name: имя объекта
        :return: путь к файлу объекта
        """
        return os.path.join(self.get_objects_path(db_name, schema_name, object_type), object_name)

    def create_folders(self, db_name, schema, obj_type):
        """
        :param db_name: наименование базы данных
        :param schema: наименование схемы
        :param obj_type: тип объекта
        """
        schema = schema['name']
        if schema not in IGNORED_SCHEMAS:
            obj_folder_path = self.get_objects_path(db_name, schema, obj_type)
            if not os.path.exists(obj_folder_path):
                os.makedirs(obj_folder_path)
            self.remove_folder(obj_folder_path)

    def create_ddl_files(self, obj, db_name, obj_type):
        """
        :param obj: содержит наименование объекта и схему
        :param db_name: наименование базы данных
        :param obj_type: тип объекта
        """
        obj_name = obj['name']
        schema_name = obj['schema_name']
        if schema_name not in IGNORED_SCHEMAS:
            filename = obj_name + '.sql'
            file_path = self.get_ddl_path(db_name, schema_name, obj_type, filename)
            ddl = self.get_ddl(db_name, schema_name, obj_name)
            with open(file_path, 'w', encoding="utf_8") as wf:
                wf.write(ddl)

    def create_ddls(self):
        """
        Обход перечисленных объектов и запись их DDL
        """
        for db_name in DATABASES:
            for obj_type in self.__obj_types:
                for schema in self.__qp.get_schemas(db_name):
                    self.create_folders(db_name, schema, obj_type)
                if obj_type == 'triggers':
                    objects = self.__qp.get_triggers(db_name)
                elif obj_type == 'functions':
                    objects = self.__qp.get_functions(db_name)
                else:
                    objects = self.__qp.get_all_objects(db_name, obj_type)
                for obj in objects:
                    self.create_ddl_files(obj, db_name, obj_type)

    def run(self):
        self.create_ddls()
