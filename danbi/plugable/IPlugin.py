import abc

class IPlugin(abc.ABC):
    def __new__(self, name):
        if not hasattr(self, 'instance'):
            self.instance = super(IPlugin, self).__new__(self)
            self._name = name
        return self.instance
    
    def getName(self):
        return self._name
    
    @abc.abstractmethod
    def getInjectionKeys(self):
        ...

    @abc.abstractmethod
    def plug(self, *args) -> None:
        ...
    
    @abc.abstractmethod
    def unplug(self) -> None:
        ...
    
    def __repr__(self):
        return self._name
