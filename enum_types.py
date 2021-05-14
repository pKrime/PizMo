from enum import Enum


class Axis(Enum):
    X = 0
    Y = 1
    Z = 2


class WidgetType(Enum):
    BONE = 0
    OPERATOR = 1


class PrimaryDrag(Enum):
    # FIXME: NOT USED YET IN THE ENUM PROPS
    NONE = 0
    TRANSLATE = 1
    ROTATE = 2
    SCALE = 3


class ShapeType(Enum):
    NONE = 0
    VERTICES = 1
    MESH = 2
    MESH3D = 3
    RECT = 4
    CIRCLE = 5
    QUAD = 6
