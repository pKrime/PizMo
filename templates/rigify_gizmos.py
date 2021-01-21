import bpy
import PizMo

from PizMo import storage, shapes, enum_types
from PizMo.storage import Stock
from PizMo.shapes import Quad2D
from PizMo.shapes import MeshShape3D
from PizMo.enum_types import ShapeType, WidgetType


def create_picker(store, obj, ctrl_name, vertex_group):
    wdg = Stock(widget_type=WidgetType.BONE,
                shape_type=ShapeType.MESH3D,
                position=(0.0, 0.0),
                data=dict(bone_name=ctrl_name,
                          object=obj,
                          vertex_group=vertex_group))

    store.add_widget(wdg)


if __name__ == "__main__":
    rigged_objs = list((ob for ob in bpy.data.objects if ob.type == 'MESH' and 'Armature' in ob.modifiers))
    max_height = max(ob.dimensions[2] for ob in rigged_objs)
    tallest = next(ob for ob in rigged_objs if ob.dimensions[2] == max_height)

    side_controls = {
        'toe.{0}': 'DEF-toe.{0}',
        'foot_ik.{0}': 'DEF-foot.{0}',
        'thigh_ik.{0}': 'DEF-thigh.{0}.001',

        'shoulder.{0}': 'DEF-shoulder.{0}',
        'upper_arm_fk.{0}': 'DEF-upper_arm.{0}.001',
        'forearm_fk.{0}': 'DEF-forearm.{0}.001',

        'hand_fk.{0}': 'DEF-palm.02.{0}',
        'thumb.01_master.{0}': 'DEF-thumb.02.{0}',
        'f_index.01_master.{0}': 'DEF-f_index.02.{0}',
        'f_middle.01_master.{0}': 'DEF-f_middle.02.{0}',
        'f_ring.01_master.{0}': 'DEF-f_ring.02.{0}',
        'f_pinky.01_master.{0}': 'DEF-f_pinky.02.{0}',
    }

    store = storage.Storage()
    for side in ['L', 'R']:
        for ctrl_name, vertex_group in side_controls.items():
            create_picker(store, tallest, ctrl_name.format(side), vertex_group.format(side))

    controls = {
        'torso': 'DEF-pelvis.{side}',
        'hips': 'DEF-spine.001',
        'chest': 'DEF-spine.003',
        'neck': 'DEF-spine.004',
        'head': 'DEF-spine.006',
    }

    for ctrl_name, vertex_group in controls.items():
        create_picker(store, tallest, ctrl_name, vertex_group)

    wdg = Stock(
        widget_type=WidgetType.BONE,
        shape_type=ShapeType.QUAD,
        position=(-0.5, -0.5),
        data=dict(bone_name='root', bone_follow=True)
    )

    store.add_widget(wdg)
