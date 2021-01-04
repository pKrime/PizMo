import PizMo

from PizMo import storage, shapes, enum_types
from PizMo.storage import Stock
from PizMo.shapes import Quad2D
from PizMo.enum_types import ShapeType, WidgetType


def create_picker():
    store = storage.Storage()
    
    wdg = Stock(widget_type=WidgetType.BONE,
                shape_type=ShapeType.VERTICES,
                position=(2.0, 0.0),
                data=dict(bone_name='ms-root', vertices=Quad2D.vertices))
    store.add_widget(wdg)

    wdg = Stock(widget_type=WidgetType.BONE,
                shape_type=ShapeType.VERTICES,
                position=(2.0, 2.0),
                data=dict(bone_name='fk-bone_9', vertices=Quad2D.vertices))

    store.add_widget(wdg)


if __name__ == "__main__":
    create_picker()
