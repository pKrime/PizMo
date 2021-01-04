from . import enum_types

from importlib import reload
reload(enum_types)

from .enum_types import WidgetType, ShapeType


class Stock:
    def __init__(self, widget_type=WidgetType.BONE, shape_type=ShapeType.NONE, data=None, position=(0, 0)):
        self.type = widget_type
        self.shape = shape_type
        self.data = data

        self.position = position


class Storage:
    _instance = None  # stores singleton instance
    _widgets = []

    @classmethod
    def exists(cls):
        return bool(cls._instance)

    def __new__(cls):
        """Singleton implementation: initialize only once, return existing instance at any subsequent attempt"""
        if cls._instance is None:
            instance = super().__new__(cls)
            cls._instance = instance

        return cls._instance

    def add_widget(self, widget):
        self._widgets.append(widget)

    def widgets(self):
        return self._widgets

    def clear(self):
        self._widgets.clear()
