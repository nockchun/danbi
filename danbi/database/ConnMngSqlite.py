from dbutils.pooled_db import PooledDB, PooledDedicatedDBConnection
from .IConnectionManager import IConnectionManager

class ConnMngSqlite(IConnectionManager):
    def connect(self, **kwargs) -> IConnectionManager:
        try:
            self.close()
            self._kwargs.update(kwargs)
            
            self._conn_pool = PooledDB(**self._kwargs)
            return self.instance
        except Exception:
            raise
    
    def isConnect(self) -> bool:
        return self._conn_pool is not None
    
    def close(self, **kwargs) -> None:
        if self._conn_pool is not None:
            self._conn_pool._close_idle()
            self._conn_pool = None
    
    def getConnection(self, auto_commit=True, **kwargs) -> PooledDedicatedDBConnection:
        try:
            conn = self._conn_pool.connection()
            return conn
        except Exception:
            raise
    
    def releaseConnection(self, conn) -> None:
        try:
            conn.close()
        except Exception:
            raise
