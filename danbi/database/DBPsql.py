from typing import Union
import pandas as pd
from .IDB import IDB

class DBPsql(IDB):
    def query(self, mapper_name: str, values: Union[dict, tuple] = None) -> list:
        raw_sql = self._mapper.get(mapper_name, values)
        
        return self.queryRaw(raw_sql, values)
    
    def queryRaw(self, raw_sql: str, values: tuple = None) -> list:
        try:
            conn = self._manager.getConnection()
            cursor = conn.cursor()

            cursor.execute(raw_sql, values)
            records = cursor.fetchall()
            
            cursor.close()
            self._manager.releaseConnection(conn)
            
            return records
        except Exception:
            if cursor is not None:
                cursor.close()
            if conn is not None:
                self._manager.releaseConnection(conn)
            raise
    
    def queryPandas(self, mapper_name: str, values: Union[dict, tuple] = None, dtype: dict = None) -> pd.DataFrame:
        raw_sql = self._mapper.get(mapper_name, values)
        
        return self.queryPandasRaw(raw_sql, values, dtype)
    
    def queryPandasRaw(self, raw_sql: str, values: Union[dict, tuple] = None, dtype: dict = None) -> pd.DataFrame:
        try:
            conn = self._manager.getConnection()
            cursor = conn.cursor()

            cursor.execute(raw_sql, values)
            records = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            
            cursor.close()
            self._manager.releaseConnection(conn)

            df = pd.DataFrame(records, columns=columns)
            
            return df if dtype is None else df.astype(dtype)
        except Exception:
            if cursor is not None:
                cursor.close()
            if conn is not None:
                self._manager.releaseConnection(conn)
            raise
    
    def execute(self, mapper_name, values=None) -> int:
        raw_sql = self._mapper.get(mapper_name, values)
        
        return self.executeRaw(raw_sql, values)
    
    def executeRaw(self, raw_sql, values=None) -> int:
        try:
            conn = self._manager.getConnection()
            cursor = conn.cursor()

            cursor.execute(raw_sql, values)
            result = cursor.rowcount
            
            cursor.close()
            self._manager.releaseConnection(conn)
            
            return result
        except Exception:
            if cursor is not None:
                cursor.close()
            if conn is not None:
                self._manager.releaseConnection(conn)
            raise
    
    def executeMany(self, mapper_name, values=None) -> int:
        raw_sql = self._mapper.get(mapper_name, values)
        
        return self.executeManyRaw(raw_sql, values)
    
    def executeManyRaw(self, raw_sql, values=None) -> int:
        try:
            conn = self._manager.getConnection()
            cursor = conn.cursor()

            cursor.executemany(raw_sql, values)
            result = cursor.rowcount
            
            cursor.close()
            self._manager.releaseConnection(conn)
            
            return result
        except Exception:
            if cursor is not None:
                cursor.close()
            if conn is not None:
                self._manager.releaseConnection(conn)
            raise
