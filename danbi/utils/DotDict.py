class DotDict:
    """
    A dictionary subclass that supports dot notation access to its keys.
    Nested dictionaries are also converted to DotDict instances.
    """

    def __init__(self, data):
        """
        Initialize the DotDict with a dictionary.
        
        Args:
            data (dict): The dictionary to convert.
        """
        for key, value in data.items():
            if isinstance(value, dict):
                # Recursively convert nested dictionaries
                setattr(self, key, DotDict(value))
            else:
                setattr(self, key, value)

    def __getattr__(self, attr):
        """
        Retrieve an attribute. Raises AttributeError if not found.
        
        Args:
            attr (str): The attribute name.
        
        Returns:
            The attribute value.
        
        Raises:
            AttributeError: If the attribute does not exist.
        """
        try:
            return self.__dict__[attr]
        except KeyError:
            raise AttributeError(f"'DotDict' object has no attribute '{attr}'")

    def __setattr__(self, key, value):
        """
        Set an attribute. If the value is a dictionary, convert it to DotDict.
        
        Args:
            key (str): The attribute name.
            value: The value to set.
        """
        if isinstance(value, dict):
            value = DotDict(value)
        self.__dict__[key] = value

    def to_dict(self):
        """
        Convert the DotDict back to a regular dictionary.
        
        Returns:
            dict: The converted dictionary.
        """
        result = {}
        for key, value in self.__dict__.items():
            if isinstance(value, DotDict):
                result[key] = value.to_dict()
            else:
                result[key] = value
        return result

    def __repr__(self):
        """
        Official string representation of DotDict.
        
        Returns:
            str: The string representation.
        """
        return f"DotDict({self.to_dict()})"

    def __iter__(self):
        """
        Make DotDict iterable by iterating over its keys.
        
        Returns:
            Iterator over the keys of the DotDict.
        """
        return iter(self.__dict__)

    def __len__(self):
        """
        Return the number of items in the DotDict.
        
        Returns:
            int: Number of key-value pairs.
        """
        return len(self.__dict__)

    def keys(self):
        """
        Return a new view of the DotDict's keys.
        
        Returns:
            dict_keys: A view object displaying a list of all the keys.
        """
        return self.__dict__.keys()

    def values(self):
        """
        Return a new view of the DotDict's values.
        
        Returns:
            dict_values: A view object displaying a list of all the values.
        """
        return self.__dict__.values()

    def items(self):
        """
        Return a new view of the DotDict's items (key, value pairs).
        
        Returns:
            dict_items: A view object displaying a list of the DotDict's key-value pairs.
        """
        return self.__dict__.items()
