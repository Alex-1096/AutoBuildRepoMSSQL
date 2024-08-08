""" Класс """
import os.path
import re
import requests
import urllib.parse

from config import *
from git import Repo
from re import match
from datetime import datetime
from getpass import getuser
from queries_processor import QueriesProcessor
from queries import upd_ver


class ScriptsCreator:

    def __init__(self):
        self.now = datetime.now().strftime("%Y-%m-%d")
        self.now = datetime.now().strftime("%Y-%m-%d")
        # Список файлов для сборки
        self.__v_file_array = BUILDS_FILES_NAMES
        # Пути
        self.__rep_path = BASE_PATH
        self.__install_tasks_path = os.path.join(self.__rep_path, 'install_tasks')
        # списки деректорий
        self.__tasks_dirs = None
        # текущая активная ветка
        self.__current_branch: str = None
        self.current_task: str = None
        self.get_branch_git()
        # Если текущая ветка НЕ мастер:
        if not self.check_build_branch():
            # создаём папку под задачу
            self.create_task_dir()
        self.get_tasks_dirs()
        self.create_tmpl_files()
        self.__qp = QueriesProcessor()

    def check_build_branch(self):
        """
        Проверяет является ли ветка билдом или мастером
        :return:
        """
        if match(pattern='master|build', string=self.__current_branch):
            return True
        return False

    def get_tasks_dirs(self) -> None:
        """
        Получает список директорий с задачами для сборки
        """
        self.__tasks_dirs = [x for x in os.listdir(self.__install_tasks_path) if os.path.isdir(os.path.join(self.__install_tasks_path, x))]

    def get_branch_git(self) -> None:
        """
        Получает наименования текущей ветки
        """
        # инициализация репозитория
        repo = Repo(self.__rep_path)
        self.__current_branch = str(repo.active_branch)

    def create_task_dir(self):
        """
        Создаёт директорию под текущую задачу, если она отсутствует
        """
        task_path = os.path.join(self.__install_tasks_path, self.__current_branch)
        if not os.path.isdir(task_path):
            os.mkdir(task_path)

    def create_tmpl_files(self):
        """
        Создание базовых файлов для сборки задач
        """
        for task in self.__tasks_dirs:
            for tpl_file_name in self.__v_file_array:
                fpath = os.path.join(self.__install_tasks_path, task, tpl_file_name)
                if not os.path.isfile(fpath):
                    with open(fpath, "w") as f:
                        pass

    def get_lines_from_file(self, fpath):
        """
        Возвращает содержимое файла построчно
        @param fpath: абсолютный путь к файлу
        """
        with open(fpath, "r", encoding="utf_8") as rf:
            return rf.readlines()

    def rewrite_file(self, fpath):
        """
        Форматирование файла
        @param fpath: абсолютный путь к файлу
        """
        lines = self.get_lines_from_file(fpath)
        if not self.__current_branch.startswith('build'):
            lines = self.set_comment_to_file(lines)
        with open(fpath, "w", encoding="utf_8") as wf:
            for line in lines:
                new_line = line.expandtabs(tabsize=4).rstrip() + '\n'
                # TODO: тут  проблема с неразрывным пробелом.
                wf.write(new_line)

    def get_comment(self):
        """
        Получение стандартного комментария
        :return: Комментарий
        """
        return f'-- {getuser()} {self.now}\n'

    def set_comment_to_file(self, lines):
        """
        Проверка наличия/создание комментария в файле
        :param lines: набор строк файла
        """
        if lines:
            if re.match(COMMENT_PATTERN, lines[0]):
                lines[0] = self.get_comment()
            else:
                lines.insert(0, self.get_comment())
            return lines
        return []

    def check_test_server(self, lines):
        for n, line in enumerate(lines):
            if re.search('sbsvcld-server9', line, re.IGNORECASE):
                raise Exception(f'В строке {n}, {line} прописан путь к тестовому серверу')

    def get_version_script(self, task_file_name):
        """
        Получает актуальную версию поставки
        @param task_file_name: абсолютный путь к файлу
        """
        main, feature, bug = self.__qp.get_cur_ver().split('.')
        if 'uninstall' not in task_file_name:
            bug = '0'
            feature = str(int(feature) + 1)
        return '.'.join([main, feature, bug])

    def create_tasks_files(self):
        """
        Сборка файлов наката и отката
        """
        print('CREATE_TASKS_FILES')
        for task in self.__tasks_dirs:
            self.current_task = task

            answer = input('right path? \n{}'.format(os.path.join(self.__install_tasks_path, task)))
            if answer.lower() not in ('n', 'т'):
                task_dir_path = os.path.join(self.__install_tasks_path, task)
                for tpl_file_name in self.__v_file_array:
                    self.create_task_file(task_dir_path, tpl_file_name)
            else:
                input('Cancel build script. Press any key')

    def install_file_processing(self, path):
        """
        Проверяет валидность указанного пути и возвращает список строк файла
        :param path: относительный путь к файлу
        :return: список строк файла
        """
        if path.startswith('source/') or path.startswith(f'install_tasks/{self.current_task}/'):
            abs_path = os.path.normpath(os.path.join(self.__rep_path, path))
            if os.path.isabs(abs_path):
                if os.path.isfile(abs_path):
                    self.rewrite_file(abs_path)
                    block = self.get_lines_from_file(abs_path)
                    return block
                else:
                    raise Exception(f'Файла по пути {abs_path} не существует')
            else:
                raise Exception(f'Путь к файлу {abs_path} не является абсолютным')
        else:
            raise Exception(f'Недопустимый путь к файлу {path}')

    def uninstall_file_processing(self, path):
        """
        Проверяет наличие файла в удаленном репозитории и возвращает список строк файла
        :param path: относительный путь к файлу
        :return: список строк файла
        """
        if path.startswith(f'install_tasks/{self.current_task}/'):
            abs_path = os.path.normpath(os.path.join(self.__rep_path, path))
            if os.path.isabs(abs_path):
                if os.path.isfile(abs_path):
                    block = self.get_lines_from_file(abs_path)
                    return block
                else:
                    raise Exception(f'Файла по пути {abs_path} не существует')
            raise Exception(f'Путь к файлу {abs_path} не является абсолютным')
        else:
            git_file_path = urllib.parse.urljoin(BASE_GIT_LINK, path)
            response = requests.get(git_file_path)

            if response.status_code == 200:
                return self.get_lines_from_git(response)
            elif response.status_code == 404:
                raise Exception(f'В удаленном репозитории нет файла  по пути {git_file_path}')
            else:
                response.raise_for_status()

    def get_lines_from_git(self, response):
        """
        Возвращает список строк файла из удаленного репозитория
        :param response: ответ get запроса по пути к файлу
        :return: список строк файла с кодом из удаленного репозитория
        """
        lines = response.text.split('\n')
        lines_list = [string + '\n' for string in lines]
        return lines_list

    def create_task_file(self, task_dir_path, tpl_file_name):
        """
        Сборка файлов наката или отката
        :param task_dir_path: Путь к папке с файлами отката и наката по задаче
        :param tpl_file_name: Название tpl файла
        :return:
        """
        source_file_path = os.path.join(task_dir_path, tpl_file_name)
        target_file_path = source_file_path.replace('_tpl', '')
        with open(target_file_path, 'w', encoding="utf_8") as wf:
            lines = self.get_lines_from_file(source_file_path)
            for line in lines:
                if line.startswith(FILE_MASK):
                    line = line.rstrip('\n')
                    path = line.replace(FILE_MASK, '')
                    if tpl_file_name == 'install_tpl.sql':
                        block = self.install_file_processing(path)

                    elif tpl_file_name == 'uninstall_tpl.sql':
                        block = self.uninstall_file_processing(path)

                    # проверяем, есть ли в коде пути на тестовый сервер
                    if self.check_build_branch():
                        self.check_test_server(block)

                    wf.write(''.join(block) + '\n')
                else:
                    wf.write(line)
                    continue
            print('END ' + target_file_path)

    def create_build_files(self):
        print('CREATE_BUILD_FILES')
        for tpl_file_name in self.__v_file_array:
            task_file_name = tpl_file_name.replace('_tpl', '')
            task_file_path = os.path.join(self.__install_tasks_path, task_file_name)
            new_version = self.get_version_script(task_file_name)
            with open(task_file_path, 'w', encoding="utf_8") as wf:
                wf.write(self.get_comment())
                if 'changed_objects.txt' not in task_file_path:
                    wf.write(upd_ver.format(new_version) + '\n')
                for branch_folder_name in self.__tasks_dirs:
                    source_file_path = os.path.join(self.__install_tasks_path, branch_folder_name, task_file_name)
                    with open(source_file_path, 'r', encoding="utf_8") as rf:
                        text = rf.read()
                        wf.write(text + '\n')
            print('END ' + task_file_name)

    def run(self):
        self.create_tasks_files()
        self.create_build_files()
