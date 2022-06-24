import sys, re
import pkgutil

if sys.version_info >= (3, 8):
    from importlib import metadata as importlib_metadata
else:
    import importlib_metadata

def infoInstalledPackage(name: str = None, version: str = None, license: str = None) -> list:
    """ Find information about all packages installed on the system.

    Args:
        name (str, optional): regular expression of packages name. Defaults to None.
        version (str, optional): regular expression of packages version. Defaults to None.
        license (str, optional): regular expression of packages license. Defaults to None.

    Returns:
        _type_: list of tuple. like '[(name, version, license)]'
    """
    regex_name = re.compile(name, re.I) if name else None
    regex_version = re.compile(version, re.I) if version else None
    regex_license = re.compile(license, re.I) if license else None
    
    dists = importlib_metadata.distributions()
    results = []
    for dist in dists:
        name = dist.metadata["Name"]
        version = dist.version
        license = dist.metadata["License"]
        
        if regex_license and not license: continue
        if regex_name and not bool(regex_name.search(name)): continue
        if regex_version and not bool(regex_version.search(version)): continue
        if regex_license and not bool(regex_license.search(license)): continue
        
        results.append((name, version, license))
    
    return results

def infoSubmodules(base: str = None, package: bool = True, include_path: bool = False) -> list:
    """Find all sub-module name or sub-package name.

    Args:
        base (str, optional): base name of package. Defaults to None.
        package (bool, optional): true to find package name, false to find file name. Defaults to True.
        include_path (bool, optional): true if you want to append the path name to the result.. Defaults to False.

    Returns:
        list: list of sub-module or sub-package name
    """
    pkg_base = __import__(base, fromlist=["blah"])
    results = []
    for loader, module_name, is_pkg in pkgutil.walk_packages(pkg_base.__path__, pkg_base.__name__ + "."):
        if is_pkg is package:
            results.append([loader.path, module_name] if include_path else module_name)
    return results