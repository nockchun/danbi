from psycopg2 import pool, extensions
from .IDBManager import IDBManager

class DBManagerPostgresql(IDBManager):
    def connect(self, **kwargs) -> IDBManager:
        try:
            self.close()
            self._kwargs.update(kwargs)
            
            self._conn_pool = pool.ThreadedConnectionPool(**self._kwargs)
            return self.instance
        except Exception:
            raise
    
    def close(self, **kwargs) -> None:
        if self._conn_pool is not None:
            self._conn_pool.closeall()
    
    def getConnection(self, auto_commit=True, **kwargs) -> extensions.connection:
        try:
            conn = self._conn_pool.getconn()
            conn.set_isolation_level(extensions.ISOLATION_LEVEL_AUTOCOMMIT if auto_commit else extensions.ISOLATION_LEVEL_DEFAULT)
            return conn
        except Exception:
            raise
    
    def releaseConnection(self, conn) -> None:
        try:
            self._conn_pool.putconn(conn)
        except Exception:
            raise