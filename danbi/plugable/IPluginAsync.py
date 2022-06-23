import abc

class IPluginAsync(abc.ABC):
    def __new__(self, name):
        if not hasattr(self, 'instance'):
            self.instance = super(IPluginAsync, self).__new__(self)
            self._name = name
        return self.instance
    
    def getName(self):
        return self._name
    
    @abc.abstractmethod
    def plug(self, **kwargs) -> bool:
        ...
    
    @abc.abstractmethod
    def unplug(self, **kwargs) -> bool:
        ...
    
    def __repr__(self):
        return self._name
