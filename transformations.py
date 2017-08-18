"""Module with utilities for transformations of JSON trees."""

import inspect

from abc import ABCMeta, abstractmethod
from collections import OrderedDict
from collections.abc import Sequence, Mapping
from utils import lookup

class NotInterested(Exception):
    pass

class check:
    def __init__(self, *args):
        self._res = lookup(*args)
    def __eq__(self, other):
        if not self._res == other:
            raise NotInterested()
    def of(self, *others):
        if not self._res in others:
            raise NotInterested()

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
            return obj

class NodeTransformation(Transformation):
    """Transformations which acts on certain dictionaries."""

    @abstractmethod
    def transform_dict(self, obj):
        """Computes new dictionary which shall be used in tree instead of the
        node `obj`."""
        raise NotImplementedError

    def act_on_dict(self, obj):
        try:
            return self.transform_dict(obj)
        except NotInterested:
            return super().act_on_dict(obj)

class NodeTypeTransformation(NodeTransformation):
    """Transformation based on the attribute `"type"` of the node
    dictionary."""

    def transform_dict(self, obj):
        if not "type" in obj:
            raise NotInterested()
        try:
            return getattr(self, "transform_" + obj["type"])(obj)
        except AttributeError:
            return self.default_transformation(obj)

    def default_transformation(self, obj):
        """Default transformation for the case no suitable transformation was
        found."""
        raise NotInterested()

class DeleteTransformation(Transformation):

    def shall_delete(self, obj):
        if isinstance(obj, Mapping):
            return self.shall_delete_dict(obj)
        elif isinstance(obj, Sequence):
            return self.shall_delete_list(obj)
        else:
            return False

    def shall_delete_dict(self, obj):
        return False

    def shall_delete_list(self, lst):
        return False

    def shall_delete_property(self, key):
        return False

    def act_on_dict(self, obj):
        return {k: self(v) for k, v in obj.items() if not self.shall_delete(v)\
                    and not self.shall_delete_property(k)}

    def act_on_list(self, lst):
        return [self(x) for x in lst if not self.shall_delete(x)]
