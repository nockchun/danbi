import abc

class IDBManager(abc.ABC):
    def __new__(self, **kwargs):
        if not hasattr(self, 'instance'):
            self.instance = super(IDBManager, self).__new__(self)
            self._kwargs = kwargs
            self._conn_pool = None
        return self.instance
    
    @abc.abstractclassmethod
    def connect(self, **kwargs):
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
