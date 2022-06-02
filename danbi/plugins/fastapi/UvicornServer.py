from typing import Any
from enum import Enum, auto

import uvicorn
from starlette.middleware.cors import CORSMiddleware
from pydantic import BaseSettings

from danbi import plugable

class Settings(BaseSettings):
    NAME               : str  = "danbi.plugins.fastapi.UvicornServer.UvicornServer"
    OPTION_ORIGIN      : bool = True

    APP                : Any
    APP_NAME           : str  = "server:app"
    APP_PORT           : int  = 8000
    APP_HOST           : str  = "0.0.0.0"
    APP_RELOAD         : bool = True
    APP_DEBUG          : bool = True
    APP_WORKS          : int  = 5

    ORIGIN_LIST        : list = []
    ORIGIN_CREDENTIALS : bool = True
    ORIGIN_METHODS     : list = ["*"]
    ORIGIN_HEADERS     : list = ["*"]
    
settings = Settings()

class UvicornServer(plugable.IPlugin):
    def plug(self) -> bool:

        if (settings.OPTION_ORIGIN):
             self._setOrigins()

        self._startUvicorn()
    
    def unplug(self) -> bool:
        print(f"{self.getName()} unpluged.")
        
    def _setOrigins(self):
        settings.APP.add_middleware(
            CORSMiddleware,
            allow_origins=[str(origin) for origin in settings.ORIGIN_LIST],
            allow_credentials=settings.ORIGIN_CREDENTIALS,
            allow_methods=settings.ORIGIN_METHODS,
            allow_headers=settings.ORIGIN_HEADERS
        )
    
    def _startUvicorn(self):
        uvicorn.run(app=settings.APP_NAME,
            host=settings.APP_HOST,
            port=settings.APP_PORT,
            reload=settings.APP_RELOAD,
            debug=settings.APP_DEBUG,
            workers=settings.APP_WORKS
        )
