"""Module with utilities for transformations of JSON trees."""

import collections.abc

class JSONTransformation():
    """Base class of a transformation of a JSON object. This class implements
    the identity transformation. It returns a new copy of the given JSON
    object."""

    def transform_str(self, data):
        """Transforms the string `data`."""
        return data

    def transform_dict(self, obj):
        """Transforms the dictionary `obj`."""
        return {name: self(value) for name, value in obj.items()}

    def transform_list(self, lst):
        """Transforms the list `lst`."""
        return [self(element) for element in lst]

    def __call__(self, obj):
        """Transforms the JSON object `obj`."""
        if isinstance(obj, str):
            return self.transform_str(obj)
        elif isinstance(obj, collections.abc.Sequence):
            return self.transform_list(obj)
        elif isinstance(obj, collections.abc.Mapping):
            return self.transform_dict(obj)
        else:
            raise NotImplementedError
