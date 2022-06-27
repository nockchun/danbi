import abc
from typing import Any

class IMapper(abc.ABC):

    @abc.abstractclassmethod
    def setConfigPaths(self, conf_paths: list = None):
        ...
    
    @abc.abstractclassmethod
    def getConfigPaths(self) -> list:
        ...
    
    @abc.abstractclassmethod
    def setNamespaceTag(self, namespace: str, tag: str, base_package: str = None) -> None:
        ...
    
    @abc.abstractclassmethod
    def get(self, name: str, values: Any = None) -> str:
        ...

