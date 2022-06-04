from typing import Any
from enum import Enum, auto

import uvicorn
from starlette.middleware.cors import CORSMiddleware
from pydantic import BaseSettings

from danbi import plugable

class Settings(BaseSettings):
    NAME                   : str  = "danbi.plugins.fastapi.UvicornServer.UvicornServer"
    OPTION_ORIGIN          : bool = True

    UVICORN_APP_NAME       : str  = "server:app"
    UVICORN_HOST           : str  = "0.0.0.0"
    UVICORN_PORT           : int  = 8000
    UVICORN_RELOAD         : bool = True
    UVICORN_DEBUG          : bool = True
    UVICORN_SERVER_HEADER  : bool = False
    UVICORN_WORKS          : int  = 5

    ORIGIN_LIST            : list = []
    ORIGIN_CREDENTIALS     : bool = True
    ORIGIN_METHODS         : list = ["*"]
    ORIGIN_HEADERS         : list = ["*"]

class UvicornServer(plugable.IPlugin):
    settings = Settings()

    def plug(self, **kwargs) -> bool:
        assert "app" in kwargs, f"set the fastapi app when create the PluginManager.\n{' '*16}ex) PluginManager(app=<your fastapi app instance>)"

        if (UvicornServer.settings.OPTION_ORIGIN):
             self._setOrigins(kwargs["app"])

        self._startUvicorn()
    
    def unplug(self, **kwargs) -> bool:
        print(f"{self.getName()} unpluged. {kwargs}")
        
    def _setOrigins(self, app):
        app.add_middleware(
            CORSMiddleware,
            allow_origins     = [str(origin) for origin in UvicornServer.settings.ORIGIN_LIST],
            allow_credentials = UvicornServer.settings.ORIGIN_CREDENTIALS,
            allow_methods     = UvicornServer.settings.ORIGIN_METHODS,
            allow_headers     = UvicornServer.settings.ORIGIN_HEADERS
        )
    
    def _startUvicorn(self):
        uvicorn.run(
            app           = UvicornServer.settings.UVICORN_APP_NAME,
            host          = UvicornServer.settings.UVICORN_HOST,
            port          = UvicornServer.settings.UVICORN_PORT,
            reload        = UvicornServer.settings.UVICORN_RELOAD,
            debug         = UvicornServer.settings.UVICORN_DEBUG,
            server_header = UvicornServer.settings.UVICORN_SERVER_HEADER,
            workers       = UvicornServer.settings.UVICORN_WORKS
        )
