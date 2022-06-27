import asyncpg
from .IConnectionManager import IConnectionManager

class ConnMngPsqlAsync(IConnectionManager):
    async def connect(self, **kwargs) -> IConnectionManager:
        try:
            await self.close()
            self._kwargs.update(kwargs)
            
            self._conn_pool = await asyncpg.create_pool(**self._kwargs)
            return self.instance
        except Exception:
            raise
    
    def isConnect(self) -> bool:
        return self._conn_pool is not None
    
    async def close(self, **kwargs) -> None:
        if self._conn_pool is not None:
            await self._conn_pool.close()
    
    async def getConnection(self, **kwargs) -> asyncpg.pool.PoolConnectionProxy:
        try:
            conn = await self._conn_pool.acquire()
            return conn
        except Exception:
            raise
    
    async def releaseConnection(self, conn) -> None:
        try:
            await self._conn_pool.release(conn)
        except Exception:
            raise