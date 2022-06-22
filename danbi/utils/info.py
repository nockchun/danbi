import sys, re

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
