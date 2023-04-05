import abc
import collections
import itertools
from typing import Any, Dict, Tuple, List, Union
import pandas as pd
from multiprocessing import Lock

from .IConnectionManager import IConnectionManager
from ..mapping.IMapper import IMapper

class IDB(abc.ABC):
    def __new__(self, manager: IConnectionManager, mapper: IMapper):
        self._manager = manager
        self._mapper = mapper
        self._lock_q = Lock()
        self._lock_qr = Lock()
        self._lock_qp = Lock()
        self._lock_qpr = Lock()
        self._lock_e = Lock()
        self._lock_er = Lock()
        self._lock_em = Lock()
        self._lock_emr = Lock()

        if not hasattr(self, 'instance'):
            self.instance = super(IDB, self).__new__(self)
        return self.instance

    def _pyformat2psql(self, query: str, named_args: Dict[str, Any]) -> Tuple[str, List[Any]]:
        positional_generator = itertools.count(1)
        positional_map = collections.defaultdict(lambda: '${}'.format(next(positional_generator)))
        formatted_query = query % positional_map
        positional_items = sorted(
            positional_map.items(),
            key=lambda item: int(item[1].replace('$', '')),
        )
        positional_args = [named_args[named_arg] for named_arg, _ in positional_items]
        return formatted_query, positional_args

    def getManager(self) -> IConnectionManager:
        """
        Returns:
            IConnectionManager: danbi's database connection control manager.
        """
        return self._manager
    
    def getMapper(self) -> IMapper:
        """
        Returns:
            IMapper: danbi's Jinja2Mapper control manager.
        """
        return self._mapper
    
    @abc.abstractmethod
    def query(self, mapper_name: str, values: Union[dict, tuple] = None, print_sql: bool = False) -> list:
        """query with Jinja2Mapper's query key.

        Args:
            mapper_name (str): key value of yaml file of Jinja2Mapper.
            values (Union[dict, tuple], optional): parameter values for sql and mapper. Defaults to None.

        Returns:
            list: result of query
        """
        ...
    
    @abc.abstractmethod
    def queryRaw(self, raw_sql: str, values: tuple = None) -> list:
        """query with raw sql.

        Args:
            raw_sql (str): query sql from raw string.
            values (tuple, optional): parameter values for sql. Defaults to None.

        Returns:
            list: result of query
        """
        ...
    
    @abc.abstractmethod
    def queryPandas(self, mapper_name: str, values: Union[dict, tuple] = None, dtype: dict = None, print_sql: bool = False) -> pd.DataFrame:
        """query with Jinja2Mapper's query key. and the result type change to pandas dataframe.

        Args:
            mapper_name (str): key value of yaml file of Jinja2Mapper.
            values (Union[dict, tuple], optional): parameter values for sql and mapper. Defaults to None.
            dtype (dict, optional): pandas column's data type. The name of the column depends on the contents of the select clause of the query.  Defaults to None.

        Returns:
            pd.DataFrame: pandas dataframe.
        """
        ...
    
    @abc.abstractmethod
    def queryPandasRaw(self, raw_sql: str, values: Union[dict, tuple] = None, dtype: dict = None) -> pd.DataFrame:
        """query with raw sql query by raw_sql. and the result type change to pandas dataframe.

        Args:
            raw_sql (str): query sql from raw string.
            values (Union[dict, tuple], optional): parameter values for sql and mapper. Defaults to None.
            dtype (dict, optional): pandas column's data type. The name of the column depends on the contents of the select clause of the query. Defaults to None.

        Returns:
            pd.DataFrame: pandas dataframe.
        """
        ...
    
    @abc.abstractmethod
    def execute(self, mapper_name: str, values: Union[dict, tuple] = None, print_sql: bool = False) -> int:
        """all sqls without a result table.

        Args:
            mapper_name (str): key value of yaml file of Jinja2Mapper.
            values (Union[dict, tuple], optional): parameter values for sql and mapper. Defaults to None.

        Returns:
            int: The number of results executed.
        """
        ...
    
    @abc.abstractmethod
    def executeRaw(self, raw_sql: str, values: Union[dict, tuple] = None) -> int:
        """all sqls without a result table with raw sql string.

        Args:
            raw_sql (str): query sql from raw string.
            values (Union[dict, tuple], optional): parameter values for sql and mapper. Defaults to None.

        Returns:
            int: The number of results executed.
        """
        ...
    
    @abc.abstractmethod
    def executeMany(self, mapper_name: str, values: Union[dict, tuple] = None, print_sql: bool = False) -> int:
        """When inserting a lot of data in batches with Jinja2Mapper's query key.

        Args:
            mapper_name (str): key value of yaml file of Jinja2Mapper.
            values (Union[dict, tuple], optional): parameter values for sql and mapper. Defaults to None.

        Returns:
            int: The number of results executed.
        """
        ...
    
    @abc.abstractmethod
    def executeManyRaw(self, raw_sql: str, values: Union[dict, tuple] = None) -> int:
        """hen inserting a lot of data in batches with raw sql string.

        Args:
            raw_sql (str): query sql from raw string.
            values (Union[dict, tuple], optional): parameter values for sql and mapper. Defaults to None.

        Returns:
            int: The number of results executed.
        """
        ...
