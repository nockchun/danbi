from typing import Any, Union

from tortoise import Tortoise
from tortoise.contrib.fastapi import register_tortoise
from pydantic import BaseSettings

from danbi import plugable
from danbi.mapping import Jinja2Mapper
from danbi.database import IConnectionManager, ConnMngPsql, DBPsql

class Settings(BaseSettings):
    NAME                   : str  = "danbi.plugins.fastapi.TortoiseORM.TortoiseORM"

    DB_ENGINE: str                      = "tortoise.backends.asyncpg"
    DB_HOST: str                        = ""
    DB_NAME: str                        = ""
    DB_USER: str                        = ""
    DB_PASS: str                        = ""
    DB_PORT: int                        = 5432
    DB_POOL_MAX: int                    = 10

    ORM_MODELS: list                    = []

    JINJA2MAPPER: bool                  = False
    JINJA2MAPPER_CONFS: list            = []
    JINJA2MAPPER_NAMESPACE: str         = None
    JINJA2MAPPER_TAG: Union[str, float] = None

class TortoiseORM(plugable.IPlugin):
    settings = Settings()

    def plug(self, **kwargs) -> bool:
        assert "app" in kwargs, f"set the fastapi app when create the PluginManager.\n{' '*16}ex) PluginManager(app=<your fastapi app instance>)"

        app = kwargs["app"]

        self._connect(app)
        if TortoiseORM.settings.JINJA2MAPPER:
            self._raw_connect(app)
    
    def unplug(self, **kwargs) -> bool:
        print(f"{self.getName()} unpluged. {kwargs}")
    
    def _connect(self, app):
        conn_mng = ConnMngTortoise().connect(app=app)

    def _raw_connect(self, app):
        psql = ConnMngPsql(
            user="rsnet",
            password="rsnet",
            host="postgresql-hl.postgresql",
            port="5432",
            database="rsnet"
        ).connect(minconn=1, maxconn=2)
        mapper = Jinja2Mapper(
            TortoiseORM.settings.JINJA2MAPPER_CONFS,
            TortoiseORM.settings.JINJA2MAPPER_NAMESPACE,
            TortoiseORM.settings.JINJA2MAPPER_TAG
        )
        app.tortoise = DBPsql(psql, mapper)

class ConnMngTortoise(IConnectionManager):
    def connect(self, **kwargs) -> IConnectionManager:
        app = kwargs["app"]
        
        try:
            config = {
                "connections": {
                    "danbi": {
                        "engine": TortoiseORM.settings.DB_ENGINE,
                        "credentials": {
                            "host": TortoiseORM.settings.DB_HOST,
                            "database": TortoiseORM.settings.DB_NAME,
                            "user": TortoiseORM.settings.DB_USER,
                            "password": TortoiseORM.settings.DB_PASS,
                            "port": TortoiseORM.settings.DB_PORT
                        },
                        "maxsize": TortoiseORM.settings.DB_POOL_MAX
                    }
                },
                "apps": {
                    "stofacker": {
                        "models": TortoiseORM.settings.ORM_MODELS,
                        "default_connection": "danbi"
                    }
                }
            }
            register_tortoise(
                app,
                config=config,
                generate_schemas=True,
                add_exception_handlers=True
            )
            return self.instance
        except Exception:
            raise
    
    def close(self, **kwargs) -> None:
        ...
    
    def getConnection(self, auto_commit=True, **kwargs):
        try:
            return Tortoise.get_connection("danbi")
        except Exception:
            raise
    
    def releaseConnection(self, conn) -> None:
        ...
