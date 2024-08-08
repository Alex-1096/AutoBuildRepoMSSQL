from scripts_creator import ScriptsCreator
from ddl_refresher import DDLRefresher
from rebuild_ddl import RebuildDDL
import argparse


def create_scripts():
    """
    Запуск обработчика создания скриптов миграции
    """
    creator = ScriptsCreator()
    # Запись файлов
    creator.run()
    print('SUCCESS')
    answer = input()


def update_ddls():
    """
    Запуск обработчика создания/обновления DDL
    """
    ddl_refresher = DDLRefresher()
    ddl_refresher.run()
    print('SUCCESS')
    answer = input()


def rebuild_repos():
    """
    Запуск процедуры актуализации репозитория
    """
    rebuild_repos = RebuildDDL()
    rebuild_repos.run()
    print('SUCCESS')
    answer = input()


def main():
    """
    Выбор логики выполнения программы
    """
    try:
        parser = argparse.ArgumentParser(
            description="Сценарий выполнения скрипта: сборка скриптов миграции или сборка DDL")
        parser.add_argument("entry_point", help="Имя сценария")
        args = parser.parse_args()
        entry_point = args.entry_point
    except:
        entry_point = ""
    while True:
        if entry_point == 'create_scripts':
            create_scripts()
            break
        elif entry_point == 'update_ddls':
            update_ddls()
            break
        elif entry_point == 'rebuild_repos':
            rebuild_repos()
            break
        elif entry_point == 'exit':
            break
        else:
            print('введите подходящую точку входа или exit:')
            entry_point = input()


if __name__ == '__main__':
    main()
