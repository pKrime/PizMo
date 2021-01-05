import bpy
import PizMo

from PizMo import storage, shapes, enum_types
from PizMo.storage import Stock
from PizMo.shapes import Quad2D
from PizMo.shapes import MeshShape
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
                position=(0.0, 0.0),
                data=dict(bone_name='ik-bone_33.L',
                          vertices=MeshShape(bpy.data.objects['GEO-all'],
                                             scale=2.0).vertices, ))

    store.add_widget(wdg)

    wdg = Stock(widget_type=WidgetType.BONE,
                shape_type=ShapeType.VERTICES,
                position=(0.0, 0.0),
                data=dict(bone_name='ik-bone_33.L',
                          vertices=MeshShape(bpy.data.objects['GEO-all'],
                                             scale=2.0).vertices,))

    store.add_widget(wdg)

    wdg = Stock(widget_type=WidgetType.BONE,
                shape_type=ShapeType.VERTICES,
                position=(0.0, 0.0),
                data=dict(bone_name='ik-bone_33.R', vertices=MeshShape(bpy.data.objects['GEO-all'],
                                                                       vertex_group='bone_33.R',
                                                                       scale=2.0).vertices))

    store.add_widget(wdg)



if __name__ == "__main__":
    create_picker()
