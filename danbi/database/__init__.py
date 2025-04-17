from .IConnectionManager import IConnectionManager
from .ConnMngPsql import ConnMngPsql
from .ConnMngSqlite import ConnMngSqlite
from .IDB import IDB
from .DBPsql import DBPsql
from .DBSqlite import DBSqlite
from .ConnMngPsqlAsync import ConnMngPsqlAsync
from .DBPsqlAsync import DBPsqlAsync
from .factory import (
    usePgDBMapper, usePgDBMapperAsync
)
import sqlite3
from ..mapping import Jinja2Mapper

psql: IDB = DBPsql(ConnMngPsql(), Jinja2Mapper())
def setPsql(user: str, password: str, host: str, port: int, database: str, pool_min: int, pool_max: int, mappers: list = None, namespace: str = None, tag: str = None, base_package: str = None):
    if psql.getMapper().getConfigPaths() is None and mappers is not None and base_package is not None:
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

sqlite: IDB = DBSqlite(ConnMngSqlite(), Jinja2Mapper())
def setSqlite(database: str, pool_min: int, pool_max: int, mappers: list = None, namespace: str = None, tag:str = None, base_package: str = None):
    if sqlite.getMapper().getConfigPaths() is None and mappers is not None and base_package is not None:
        sqlite.getMapper().setConfigPaths(mappers).setNamespaceTag(namespace, tag, base_package)
    if not sqlite.getManager().isConnect():
        sqlite.getManager().connect(
            creator=sqlite3,
            database=database,
            maxconnections=pool_max,
            mincached=pool_min,
            isolation_level=None
        )