import abc
import pandas as pd
from .IDBManager import IDBManager
from ..mapping.IMapper import IMapper

class DB(abc.ABC):
    def __new__(self, manager: IDBManager, mapper: IMapper):
        if not hasattr(self, 'instance'):
            self.instance = super(DB, self).__new__(self)
            self._manager = manager
            self._mapper = mapper
        return self.instance
    
    def getManager(self):
        return self._manager
    
    @abc.abstractmethod
    def query(self, mapper_name, values=None) -> list:
        ...
    
    @abc.abstractmethod
    def queryRaw(self, raw_sql, values=None) -> list:
        ...
    
    @abc.abstractmethod
    def queryPandas(self, mapper_name, values=None, dtype: dict = None) -> pd.DataFrame:
        ...
    
    @abc.abstractmethod
    def queryPandasRaw(self, mapper_name, values=None, dtype: dict = None) -> pd.DataFrame:
        ...
    
    @abc.abstractmethod
    def execute(self, mapper_name, values=None) -> int:
        ...
    
    @abc.abstractmethod
    def executeRaw(self, raw_sql, values=None) -> int:
        ...
    
    @abc.abstractmethod
    def executeMany(self, mapper_name, values=None) -> int:
        ...
    
    @abc.abstractmethod
    def executeManyRaw(self, raw_sql, values=None) -> int:
        ...
