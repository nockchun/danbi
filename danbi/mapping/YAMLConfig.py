from typing import Any, Union
import yaml
import os, glob

class YAMLConfig:
    """ Manage various config file with yaml file.
    """
    def __init__(self, conf_paths: list = []):
        """
        Args:
            conf_paths (list, optional): file or directory path for yaml config file. Defaults to [].
        """
        assert isinstance(conf_paths, list), "param 'conf_paths' have to a list"
        self._configs = []
        self._current = []
        
        first_name, first_tag = None, None
        for idx, conf_file in enumerate(self._parsePaths(conf_paths)):
            config = {}
            config["path"] = conf_file
            config["configs"] = []
            with open(conf_file, "r") as stream:
                configs_raw = yaml.safe_load_all(stream)
                for data in configs_raw:
                    config["configs"].append(data)
                    first_name = data["namespace"]
                    first_tag = data["tag"]
            self._configs.append(config)
        self.setCurrent(first_name, first_tag)
    
    def _parsePaths(self, conf_paths: list = []) -> list:
        all_paths = []
        for conf_path in conf_paths:
            if os.path.isfile(conf_path):
                all_paths.append(conf_path)
            elif os.path.isdir(conf_path):
                for conf_file in glob.glob(conf_path+"/*.yaml"):
                    all_paths.append(conf_file)
        return all_paths
    
    def getSignatures(self) -> list:
        """
        Returns:
            list: all (namespace, tag, path)
        """
        signatures = []
        for config_meta in self._configs:
            for config in config_meta["configs"]:
                signatures.append((config["namespace"], config["tag"], config_meta["path"]))
        
        return signatures
    
    def getConfig(self, namespace: str, tag: Any) -> dict:
        """Search for settings of config file with the same "name:tag".
        Args:
            namespace (str): namespace of configs
            tag (str): tag/version of configs
        Raises:
            Exception: Occurs when searching for "name:tag" that does not exist.
        Returns:
            dict: all config information.
        """
        result = []
        for config in self._findConfig(namespace, tag)["configs"]:
            result.append(config["config"])
        return result
    
    def _findConfig(self, namespace: str, tag: Any) -> dict:
        result = {"configs": []}
        for config_meta in self._configs:
            for config in config_meta["configs"]:
                if config["namespace"] == namespace and config["tag"] == tag:
                    result["namespace"] = namespace
                    result["tag"] = tag
                    result["configs"].append({
                        "path": config_meta["path"],
                        "config": config
                    })
        
        if len(result["configs"]) == 0:
            raise Exception(f"There is no sutable data.")
        else:
            return result
    
    def setCurrent(self, namespace: str, tag: Any):
        """Set the signature ("namespace:tag") to use. 
        Args:
            namespace (str): namespace of config.
            tag (str): tag or version of config.
        """
        self._current = self._findConfig(namespace, tag)

        return self
    
    def getCurrent(self) -> dict:
        """Get all configuration variables existing in the "namespace:tag" specified by the setCurrent() method.
        Returns:
            dict: all configuration variables.
        """
        result = []
        for config in self._current["configs"]:
            result.append(config["config"])
        
        return result
    
    def __genCmdString(self, dot_query: str) -> str:
        command = "config['config']"
        for element in dot_query.split("."):
            try:
                array = element[element.index("["):]
                element = element[:element.index("[")]
            except Exception:
                array = None
                pass

            command += f"['{element}']"
            if array is not None:
                command += array
        return command
    
    def getValue(self, dot_query: str) -> str:
        """The value of the configuration variables in the "namespace:tag" specified by the setCurrent() method.
        Args:
            dot_query (str): variable position using dot notation.
            ex) a.b[1].c
        Returns:
            str: the value of the position.
        """
        result = []
        for config in self._current["configs"]:
            result.append(eval(self.__genCmdString(dot_query)))
        return result
    
    def setValue(self, dot_query: str, value: Union[tuple, dict, list]) -> None:
        """Set the value at the location of the variable using dot notation.
        Args:
            dot_query (str): variable position using dot notation.
            value (str): The setting value you want to set.
        """
        for config in self._current["configs"]:
            exec(f"{self.__genCmdString(dot_query)}='{value}'")
    
    def persist(self) -> None:
        """save the current configurations to the source file.
        """
        for current in self._current["configs"]:
            for config in self._configs:
                if config["path"] == current["path"]:
                    with open(config["path"], 'w') as file:
                        yaml.dump_all(config['configs'], file)
