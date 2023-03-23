from typing import Union
import pandas as pd
from .IDB import IDB

class DBPsqlAsync(IDB):
    async def query(self, mapper_name: str, values: dict = None) -> list:
        with self._lock:
            raw_sql = self._mapper.get(mapper_name, values)
            if values is not None:
                raw_sql, values = self._pyformat2psql(raw_sql, values)
            
            return await self.queryRaw(raw_sql, values)
    
    async def queryRaw(self, raw_sql: str, values: list = None) -> list:
        try:
            with self._lock:
                conn = await self._manager.getConnection()
                if values is None:
                    records = await conn.fetch(raw_sql)
                else:
                    records = await conn.fetch(raw_sql, *values)
                await self._manager.releaseConnection(conn)
                
                return records
        except Exception:
            if conn is not None:
                await self._manager.releaseConnection(conn)
            raise
    
    async def queryPandas(self, mapper_name: str, values: Union[dict, tuple] = None, dtype: dict = None) -> pd.DataFrame:
        with self._lock:
            raw_sql = self._mapper.get(mapper_name, values)
            if values is not None:
                raw_sql, values = self._pyformat2psql(raw_sql, values)
            
            return await self.queryPandasRaw(raw_sql, values, dtype)
    
    async def queryPandasRaw(self, raw_sql: str, values: list = None, dtype: dict = None) -> pd.DataFrame:
        try:
            with self._lock:
                records = await self.queryRaw(raw_sql, values)
                if len(records) > 0:
                    df = pd.DataFrame(records, columns=records[0].keys())
                else:
                    return pd.DataFrame()
                
                return df if dtype is None else df.astype(dtype)
        except Exception:
            raise
    
    async def execute(self, mapper_name, values=None) -> None:
        with self._lock:
            raw_sql = self._mapper.get(mapper_name, values)
            await self.executeRaw(raw_sql, values)
    
    async def executeRaw(self, raw_sql, values=None) -> None:
        try:
            with self._lock:
                conn = await self._manager.getConnection()
                if values is None:
                    await conn.execute(raw_sql)
                else:
                    await conn.execute(raw_sql, *values)
                await self._manager.releaseConnection(conn)
        except Exception:
            if conn is not None:
                await self._manager.releaseConnection(conn)
            raise
    
    async def executeMany(self, mapper_name, values=None) -> None:
        with self._lock:
            raw_sql = self._mapper.get(mapper_name, values)
            await self.executeManyRaw(raw_sql, values)
    
    async def executeManyRaw(self, raw_sql, values=None) -> None:
        try:
            with self._lock:
                conn = await self._manager.getConnection()
                await conn.executemany(raw_sql, values)
                await self._manager.releaseConnection(conn)
        except Exception:
            if conn is not None:
                await self._manager.releaseConnection(conn)
            raise
