import os, pkgutil, inspect
from .IPlugin import IPlugin

class PluginManager:
    def __init__(self, base_package: str):
        self._base_package = base_package
        self._plugins = []
        self._discover_plugins(base_package)
    
    def getPlugins(self) -> list:
        return self._plugins
    
    def _discover_plugins(self, package: str) -> None:
        imported_package = __import__(package, fromlist=['blah'])
        for _, pluginname, ispkg in pkgutil.iter_modules(imported_package.__path__, imported_package.__name__ + '.'):
            if not ispkg:
                plugin_module = __import__(pluginname, fromlist=['blah'])
                clazz_members = inspect.getmembers(plugin_module, inspect.isclass)
                for (_, clazz) in clazz_members:
                    if issubclass(clazz, IPlugin) & (clazz is not IPlugin):
                        instance = clazz(f'{clazz.__module__}.{clazz.__name__}')
                        self._plugins.append(instance)
        
        all_current_paths = []
        if isinstance(imported_package.__path__, str):
            all_current_paths.append(imported_package.__path__)
        else:
            all_current_paths.extend([x for x in imported_package.__path__])
        
        seen_paths = []
        for pkg_path in all_current_paths:
            if (pkg_path not in seen_paths) and (not pkg_path.endswith("__")):
                seen_paths.append(pkg_path)
                child_pkgs = [p for p in os.listdir(pkg_path) if os.path.isdir(os.path.join(pkg_path, p))]
                for child_pkg in child_pkgs:
                    self._discover_plugins(package + '.' + child_pkg)
    
    def plug(self, injection_map: dict, target: str = None) -> None:
        for plugin in self._plugins:
            if (target is None):
                plugin.plug(*[injection_map[x] for x in plugin.getInjectionKeys()])
            elif plugin.getName == target:
                plugin.plug(*[injection_map[x] for x in plugin.getInjectionKeys()])
    
    def unplug(self) -> None:
        for plugin in self._plugins:
            plugin.unplug()
