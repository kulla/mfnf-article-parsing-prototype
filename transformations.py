"""Module with utilities for transformations of JSON trees."""

import inspect

from abc import ABCMeta, abstractmethod
from collections import OrderedDict
from collections.abc import Sequence, Mapping

class Action(metaclass=ABCMeta):
    """Base class for an action."""

    def __init__(self, **options):
        for key, value in options.items():
            setattr(self, key, value)

    @abstractmethod
    def __call__(self, arg):
        """Defines a transformation on the argument `arg`."""
        raise NotImplementedError

class ChainedActionMetaclass(ABCMeta):
    """Metaclass for class `ChainedTransformations` which add the member
    `actions` with the list of all transformations defined inside the class
    definition."""

    @classmethod
    def __prepare__(mcs, name, bases):
        return OrderedDict(super().__prepare__(mcs, name, bases))

    def __new__(mcs, name, bases, props):
        props["action_classes"] = [x for x in props.values() \
                                     if inspect.isclass(x)]

        return type.__new__(mcs, name, bases, dict(props))

class ChainedAction(Action, metaclass=ChainedActionMetaclass):
    """A transformation which combines all transformations which are defined
    inside this class."""

    action_classes = []

    def __init__(self, **options):
        super().__init__(**options)

        self.actions = [x(**options) for x in self.action_classes]

    def __call__(self, arg):
        result = arg

        for action in self.actions:
            result = action(result)

        return result

class Transformation(Action):
    """Base class of a transformation of a JSON object. This class implements
    the identity transformation. It returns a new copy of the given JSON
    object."""

    def act_on_dict(self, obj):
        """Transforms the dictionary `obj`."""
        return {name: self(value) for name, value in obj.items()}

    def act_on_list(self, lst):
        """Transforms the list `lst`."""
        return [self(element) for element in lst]

    def __call__(self, obj):
        """Transforms the JSON object `obj`."""
        if isinstance(obj, str):
            return obj
        elif isinstance(obj, Sequence):
            return self.act_on_list(obj)
        elif isinstance(obj, Mapping):
            return self.act_on_dict(obj)
        else:
            raise NotImplementedError

class NodeTransformation(Transformation):
    """Transformations which acts on certain dictionaries."""

    @abstractmethod
    def is_target_dict(self, obj):
        """Returns `True` in case this transformation shall apply on this
        node."""
        raise NotImplementedError

    @abstractmethod
    def transform_dict(self, obj):
        """Computes new dictionary which shall be used in tree instead of the
        node `obj`."""
        raise NotImplementedError

    def act_on_dict(self, obj):
        if self.is_target_dict(obj):
            return self.transform_dict(obj)
        else:
            super().act_on_dict(obj)

class NodeTypeTransformation(NodeTransformation):
    """Transformation based on the attribute `"type"` of the node
    dictionary."""

    def is_target_dict(self, obj):
        return "type" in obj

    def transform_dict(self, obj):
        method = getattr(self, "transform_" + obj["type"], None)

        if method:
            return method(obj)
        else:
            self.default_transformation(obj)

    def default_transformation(self, obj):
        """Default transformation for the case no suitable transformation was
        found."""
        return super().act_on_dict(obj)
