from jinja2 import Template
from .YAMLConfig import YAMLConfig
from .IMapper import IMapper

class Jinja2Mapper(IMapper):
    def __init__(self, conf_paths: list, namespace: str = None, tag = None):
        self._conf_paths = conf_paths
        self._mapper = {}
        if (namespace is not None) and (tag is not None):
            self.setNamespaceTag(namespace, tag)
            
    def setNamespaceTag(self, namespace: str, tag: str) -> None:
        template = YAMLConfig(self._conf_paths)
        template.setCurrent(namespace, tag)
        
        self._mapper = {}
        for config in template.getCurrent():
            for mapper in config["mapper"]:
                self._mapper[mapper["name"]] = mapper["temp"]
    
    def get(self, name: str, values=None) -> str:
        return Template(self._mapper[name]).render(values=values)