import abc

class IConnectionManager(abc.ABC):
    def __new__(self, **kwargs):
        self._kwargs = kwargs
        if not hasattr(self, 'instance'):
            self.instance = super(IConnectionManager, self).__new__(self)
            self._conn_pool = None
        return self.instance
    
    @abc.abstractclassmethod
    def connect(self, **kwargs):
        ...
    
    @abc.abstractclassmethod
    def isConnect(self) -> bool:
        ...

    @abc.abstractclassmethod
    def close(self, **kwargs):
        ...
    
    @abc.abstractclassmethod
    def getConnection(self, auto_commit=True, **kwargs):
        ...
    
    @abc.abstractclassmethod
    def releaseConnection(self, conn):
        ...
