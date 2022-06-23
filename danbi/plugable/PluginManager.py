import os, pkgutil, inspect
from .IPlugin import IPlugin
from danbi import utils

class PluginManager:
    def __init__(self, **kwargs):
        self._plugins = {}
        self._kwargs = kwargs
    
    def addPackagePath(self, path: str):
        self._discover_plugins(path)

        return self
    
    def addPackage(self, package_regex_name: str):
        packages_info = utils.infoInstalledPackage(package_regex_name)
        for package in packages_info:
            self._discover_plugins(package[0])
        
        return self

    def getPlugins(self) -> list:
        return list(self._plugins.keys())
    
    def _discover_plugins(self, package: str) -> None:
        imported_package = __import__(package, fromlist=['blah'])
        for _, pluginname, ispkg in pkgutil.iter_modules(imported_package.__path__, imported_package.__name__ + '.'):
            if not ispkg:
                plugin_module = __import__(pluginname, fromlist=['blah'])
                clazz_members = inspect.getmembers(plugin_module, inspect.isclass)
                for (_, clazz) in clazz_members:
                    if issubclass(clazz, IPlugin) & (clazz is not IPlugin):
                        full_name = f'{clazz.__module__}.{clazz.__name__}'
                        self._plugins[full_name] = [None, False, clazz]
        
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
    
    def plug(self, target: str = None) -> None:
        if target is None:
            for fullname, plugin in self._plugins.items():
                if not plugin[1]:
                    plugin[0] = plugin[2](fullname)
                    plugin[0].plug(**self._kwargs)
                    plugin[1] = True
        else:
            plugin = self._plugins[target]
            if not plugin[1]:
                plugin[0] = plugin[2](target)
                plugin[0].plug(**self._kwargs)
                plugin[1] = True
    
    def unplug(self, target: str = None) -> None:
        if target is None:
            for key, plugin in self._plugins.items():
                if plugin[1]:
                    plugin[0].unplug(**self._kwargs)
                    del plugin[0]
                    self._plugins[key] = [None, False, plugin[1]]
        else:
            plugin = self._plugins[target]
            if plugin[1]:
                plugin[0].unplug(**self._kwargs)
                del plugin[0]
                self._plugins[target] = [None, False, plugin[1]]
