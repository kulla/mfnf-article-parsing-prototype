"""Module with utilities for transformations of JSON trees."""

import inspect
import collections.abc

from collections import OrderedDict

class ChainedTransformationMetaclass(type):
    """Metaclass for class `ChainedTransformations` which add the member
    `actions` with the list of all transformations defined inside the class
    definition."""

    @classmethod
    def __prepare__(mcs, name, bases):
        return OrderedDict(super().__prepare__(mcs, name, bases))

    def __new__(mcs, name, bases, props):
        props["actions"] = [x() for x in props.values() if inspect.isclass(x)]

        return type.__new__(mcs, name, bases, dict(props))

class ChainedTransformation(metaclass=ChainedTransformationMetaclass):
    """A transformation which combines all transformations which are defined
    inside this class."""

    actions = []

    def __call__(self, arg):
        result = arg

        for action in self.actions:
            result = action(result)

        return result

class JSONTransformation():
    """Base class of a transformation of a JSON object. This class implements
    the identity transformation. It returns a new copy of the given JSON
    object."""

    def transform_dict(self, obj):
        """Transforms the dictionary `obj`."""
        return {name: self(value) for name, value in obj.items()}

    def transform_list(self, lst):
        """Transforms the list `lst`."""
        return [self(element) for element in lst]

    def __call__(self, obj):
        """Transforms the JSON object `obj`."""
        if isinstance(obj, str):
            return obj
        elif isinstance(obj, collections.abc.Sequence):
            return self.transform_list(obj)
        elif isinstance(obj, collections.abc.Mapping):
            return self.transform_dict(obj)
        else:
            raise NotImplementedError
