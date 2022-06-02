import abc

class IMapper(abc.ABC):
    @abc.abstractclassmethod
    def setNamespaceTag(self, namespace: str, tag: str) -> None:
        ...
    
    @abc.abstractclassmethod
    def get(self, name: str, values = None) -> str:
        ...

