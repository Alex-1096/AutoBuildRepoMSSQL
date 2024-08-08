from typing import Final
from dotenv import load_dotenv
import os

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')

if os.path.isfile(dotenv_path):
    load_dotenv(dotenv_path)

FILE_MASK: Final[str] = '*** '
BUILDS_FILES_NAMES: list[str] = ['install_tpl.sql', 'uninstall_tpl.sql']
COMMENT_PATTERN = r"--\s+[\w.]+\s+\d\d\d\d-\d\d-\d\d"
BASE_PATH = os.getenv('BASE_PATH')
DB_PATH = os.getenv('DB_PATH')
BASE_GIT_LINK = 'https://gitlab.keyauto.ru/dwh/dvh_ms_server/-/raw/master/'
SRV = os.getenv('SRV')
USR = os.getenv('USR')
PW = os.getenv('PW')
DATABASES = ['DWH_ETLSystem', 'OPA', 'OZCH', 'Personal', 'SB', 'SSP', 'temp_db', 'ZakNar']
OBJECT_TYPES = ['tables', 'procedures', 'views', 'triggers', 'functions']
IGNORED_SCHEMAS = ['partitions']
