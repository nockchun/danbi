from .IConnectionManager import IConnectionManager
from .ConnMngPsql import ConnMngPsql
from .IDB import IDB
from .DBPsql import DBPsql
from .ConnMngPsqlAsync import ConnMngPsqlAsync
from .DBPsqlAsync import DBPsqlAsync
from .factory import (
    usePgDBMapper, usePgDBMapperAsync
)

from ..mapping import Jinja2Mapper
psql: IDB = DBPsql(ConnMngPsql(), Jinja2Mapper())

def setPsql(user: str, password: str, host: str, port: int, database: str, pool_min: int, pool_max: int, mappers: list, namespace: str, tag, base_package: str = None):
    if psql.getMapper().getConfigPaths() is None:
        psql.getMapper().setConfigPaths(mappers).setNamespaceTag(namespace, tag, base_package)
    if not psql.getManager().isConnect():
        psql.getManager().connect(
            user=user,
            password=password,
            host=host,
            port=port,
            database=database,
            minconn=pool_min,
            maxconn=pool_max,
        )
