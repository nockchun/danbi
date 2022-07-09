from jinja2 import Template
from .YAMLConfig import YAMLConfig
from .IMapper import IMapper

class Jinja2Mapper(IMapper):
    def __init__(self, conf_paths: list = None, namespace: str = None, tag = None, base_package: str = None):
        self._conf_paths = conf_paths
        self._mapper = {}
        self._base_package = base_package
        if (namespace is not None) and (tag is not None):
            self.setNamespaceTag(namespace, tag)
    
    def setConfigPaths(self, conf_paths: list = None) -> IMapper:
        self._conf_paths = conf_paths

        return self
    
    def getConfigPaths(self) -> list:
        return self._conf_paths

    def setNamespaceTag(self, namespace: str, tag: str, base_package: str = None) -> None:
        if base_package is not None:
            self._base_package = base_package
        template = YAMLConfig(self._conf_paths, self._base_package)
        template.setCurrent(namespace, tag)
        
        self._mapper = {}
        for config in template.getCurrent():
            for mapper in config["mapper"]:
                self._mapper[mapper["name"]] = mapper["temp"]
    
    def get(self, name: str, values=None, verbose=False) -> str:
        result = Template(self._mapper[name]).render(values=values)
        if verbose:
            print(result)
        return result
