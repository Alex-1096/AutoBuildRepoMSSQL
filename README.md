![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)

# auto_builder_tasks

Проект для автоматической сборки репозитория, скриптов поставок и отката для БД MS Server

### Текущая версия интерпретатора [3.10.4](https://www.python.org/downloads/release/python-3104/)

### Зависимости указаны в файле `requirements.txt`

### Переменные окружения
Перед началом работы необходимо в корне проекта создать файл `.env` и указать значения переменных по образцу

1. BASE_PATH = 'абсолютный путь в корень репозитория сборки скриптов поставки и отката'
2. DB_PATH = 'строка подключения к базе данных'
3. SRV = 'адрес сервера базы данных'
4. USR = 'имя пользователя для доступа к базе данных'
5. PW = 'пароль для доступа к базе данных'

### Запуск

Для удобства можно настроить bat-ник, который будет запускать сборку скриптов отката 
без необходимости обращаться напрямую к файлу run.py текущего проекта
Для этого создайте файл с расширением .bat и пропишите в первой строке **через пробел без кавычек**

абсолютный_путь_к_файлу_python.exe_текущего_проекта абсолютный_путь_к_файлу_ru.py_текущего_проекта
pause()

Команда `pause` необходима только для того, чтобы после отработки скрипта консоль не закрывалась, и можно
было просмотреть результат, увидеть ошибки, если они возникнут.

#### Возможные параметры запуска
create_scripts - сборка скриптов поставки  
update_ddls - генерация ddl таблиц  
rebuild_repos - сборка репозитория  
exit - выход  
