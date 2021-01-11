import bpy
import PizMo

from PizMo import storage, shapes, enum_types
from PizMo.storage import Stock
from PizMo.shapes import Quad2D
from PizMo.shapes import MeshShape3D
from PizMo.enum_types import ShapeType, WidgetType


def create_picker(bone_widgets):
    store = storage.Storage()

    # for bone_name, wdg_mesh_name in bone_widgets.items():
    #    print('bone:', bone_name, 'mesh', wdg_mesh_name)
    #    wdg = Stock(widget_type=WidgetType.BONE,
    #                shape_type=ShapeType.MESH3D,
    #                position=(0.0, 0.0),
    #                data=dict(bone_name=bone_name,
    #                          object=bpy.data.objects[wdg_mesh_name]))

    #    store.add_widget(wdg)

    wdg = Stock(widget_type=WidgetType.BONE,
                shape_type=ShapeType.MESH3D,
                position=(0.0, 0.0),
                data=dict(bone_name='ik-bone_33.L',
                          object=bpy.data.objects['GEO-all'],
                          vertex_group='bone_33.L'))
    store.add_widget(wdg)


if __name__ == "__main__":
    bone_widgets = {
        # 'ik-bone_33.L': 'WDG-foot.L',
        'ik-poleleg.001.L': 'WDG-leg.L',
        'ik-bone_33.R': 'WDG-foot.R',
        'ik-poleleg.001.R': 'WDG-leg.R',
        'fk-root': 'WDG-belt',
        'fk-bone_9': 'WDG-belly',
        'fk-bone_17': 'WDG-torso',
        'fk-bone_18': 'WDG-neck',
        'fk-bone_19': 'WDG-head',
        'fk-bone_20': 'WDG-hair',
        'ms-root': 'WDG-hip',
        'fk-bone_21.L.L': 'WDG-shoulder.L',
        'fk-bone_21.L.R': 'WDG-shoulder.R',
        'fk-arm.001.L': 'WDG-arm.L',
        'fk-arm.002.L': 'WDG-forearm.L',
        'fk-arm.004.L': 'WDG-hand.L',
        'fk-arm.001.R': 'WDG-arm.R',
        'fk-arm.002.R': 'WDG-forearm.R',
        'fk-arm.004.R': 'WDG-hand.R'
    }

    create_picker(bone_widgets)
