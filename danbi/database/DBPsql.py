from typing import Union
import pandas as pd
from .IDB import IDB

class DBPsql(IDB):
    def query(self, mapper_name: str, values: Union[dict, tuple] = None, print_sql: bool = False) -> list:
        with self._lock_q:
            raw_sql = self._mapper.get(mapper_name, values)
            if print_sql:
                print(raw_sql)
            return self.queryRaw(raw_sql, values)
    
    def queryRaw(self, raw_sql: str, values: tuple = None) -> list:
        try:
        # with self._lock_qr:
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
    
    def queryPandas(self, mapper_name: str, values: Union[dict, tuple] = None, dtype: dict = None, print_sql: bool = False) -> pd.DataFrame:
        with self._lock_qp:
            raw_sql = self._mapper.get(mapper_name, values)
            if print_sql:
                print(raw_sql)
            return self.queryPandasRaw(raw_sql, values, dtype)
    
    def queryPandasRaw(self, raw_sql: str, values: Union[dict, tuple] = None, dtype: dict = None) -> pd.DataFrame:
        try:
        # with self._lock_qpr:
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
    
    def execute(self, mapper_name, values=None, print_sql: bool = False) -> int:
        with self._lock_e:
            raw_sql = self._mapper.get(mapper_name, values)
            if print_sql:
                print(raw_sql)
            return self.executeRaw(raw_sql, values)
    
    def executeRaw(self, raw_sql, values=None) -> int:
        try:
        # with self._lock_er:
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
    
    def executeMany(self, mapper_name, values=None, print_sql: bool = False) -> int:
        with self._lock_em:
            raw_sql = self._mapper.get(mapper_name, values)
            if print_sql:
                print(raw_sql)
            return self.executeManyRaw(raw_sql, values)
    
    def executeManyRaw(self, raw_sql, values=None) -> int:
        try:
        # with self._lock_emr:
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
