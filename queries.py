get_cur_ver = """
    use DWH_ETLSystem
    select version_num
    from dwh_version
"""

upd_ver = """
use DWH_ETLSystem
update dwh_version
set
    version_num = '{}',
    version_datetime = current_timestamp
where version_num is not null
;
"""

get_ddl_query = """
USE {};
EXEC sp_GetDDL N'{}'
"""

get_modify_tables = """
USE {0}
select
    name as table_name
from sys.[tables]
where
    type_desc = 'USER_TABLE' and
    [create_date] > getdate() - 1 or [modify_date] > getdate() - 1
"""

get_all_objects = """
USE {0}
select o.name as name, s.name as schema_name from sys.{1} o join sys.schemas s on o.schema_id = s.schema_id
"""

# берутся схемы dbo и все созданные пользователями, работает для продуктовых баз, для msdb и master
# могут вернуться лишние схемы
get_schemas = """
USE {0}
select name from sys.schemas where schema_id = 1 or schema_id  > 4 and schema_id < 16384"""

get_triggers = """
USE {0}
select t.name as name, s.name as schema_name from sys.triggers t join sys.objects o on t.parent_id = o.object_id join sys.schemas s on o.schema_id = s.schema_id"""

get_functions = """
USE {0}
select o.name as name, s.name as schema_name from sys.objects as o join sys.schemas as s on o.schema_id = s.schema_id where type IN ('FN', 'IF', 'TF', 'FS', 'FT') and is_ms_shipped = 0"""
