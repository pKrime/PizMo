import bpy
from bpy.props import PointerProperty
from bpy.props import StringProperty
from bpy.props import EnumProperty
from bpy.props import BoolProperty
from bpy.props import FloatProperty
from bpy.props import FloatVectorProperty

from . import wizmo
from importlib import reload
reload(wizmo)


def register_bone_properties():

    display_types = (
        ("mesh", "Mesh", "Object mesh"),
        ("shape", "Shape", "Geometric shape"),
        ("none", "None", "No Pizmo shape"),
    )

    shape_types = (
        ("circle", "Circle", "Circle Shape"),
        ("sphere", "Sphere", "Sphere Shape"),
        ("quad", "Quad", "Quad Shape"),
        ('none', "None", "No Shape"),
    )

    drag_action = (
        ("none", "None", "Drag doesn't do anything"),
        ("translate", "Translate", "Drag to translate"),
        ("rotate", "Rotate", "Drag to rotate"),
        ("scale", "Scale", "Drag to scale"),
    )

    bpy.types.PoseBone.pizmo_vis_type = EnumProperty(items=display_types,
                                                     name="Display Type",
                                                     default=None)

    bpy.types.PoseBone.pizmo_vis_shape = EnumProperty(items=shape_types,
                                                      name="Shape Type",
                                                      default='none')

    bpy.types.PoseBone.pizmo_drag_action = EnumProperty(items=drag_action,
                                                      name="Drag Action",
                                                      default='none')

    bpy.types.PoseBone.pizmo_alt_drag_action = EnumProperty(items=drag_action,
                                                      name="Drag Action Alt",
                                                      default='none')

    bpy.types.PoseBone.pizmo_shape_scale = FloatProperty(name="Scale of widget shape",
                                                            description="Scale the widget",
                                                            min=0.0, max=1.0, default=1.0,
                                                            update=wizmo.GrouzMo.mark_dirty)

    bpy.types.PoseBone.pizmo_shape_offset = FloatVectorProperty(name="Widgets Offset",
                                                                default=[0.0, 0.0, 0.0],
                                                                )

    bpy.types.PoseBone.pizmo_shape_frame = BoolProperty(name="Use Frame",
                                                        default=False)

    bpy.types.PoseBone.pizmo_bone_follow = BoolProperty(name="Follow Bone",
                                                        default=True)

    bpy.types.PoseBone.pizmo_vis_mesh = PointerProperty(type=bpy.types.Object,
                                                        name="Widget Mesh",
                                                        description="Object to use for widget display",
                                                        poll=lambda self, obj: obj.type == 'MESH',
                                                        update=wizmo.GrouzMo.mark_dirty)

    bpy.types.PoseBone.pizmo_vert_grp = StringProperty(name="Widget Display Group",
                                                       description="Vertices used for Selection Gizmo",
                                                       update=wizmo.GrouzMo.mark_dirty)

    bpy.types.PoseBone.pizmo_min_vertweight = FloatProperty(name="Display Group Threshold",
                                                            description="Minimum weight for displayed vertices",
                                                            min=0.0, max=1.0, default=0.2,
                                                            update=wizmo.GrouzMo.mark_dirty)


def register_armature_properties():
    armature_type = bpy.types.Armature

    armature_type.pizmo_armature_widget = BoolProperty(name="Armature Widget",
                                                       default=False,
                                                       update=wizmo.GrouzMoRoots.mark_dirty)

    armature_type.pizmo_armature_root = StringProperty(name="Armature Root Bone",
                                                      description="Bone that marks armature position in space",
                                                      update=wizmo.GrouzMoRoots.mark_dirty)

    armature_type.pizmo_color_base = FloatVectorProperty(name="Widgets Base Color",
                                                         subtype='COLOR',
                                                         default=[0.1, 0.1, 0.1],
                                                         )

    armature_type.pizmo_color_selected = FloatVectorProperty(name="Selected Widgets Color",
                                                             subtype='COLOR',
                                                             default=[0.3, 0.6, 0.7],
                                                             )

    armature_type.pizmo_color_highlight = FloatVectorProperty(name="Widgets Highlight Color",
                                                              subtype='COLOR',
                                                              default=[0.2, 0.5, 0.6],
                                                              )

    armature_type.pizmo_color_alpha = FloatProperty(name="Widgets Alpha",
                                                    min=0.0, max=1.0, default=0.25,
                                                    subtype='PERCENTAGE')

    armature_type.pizmo_color_alpha = FloatProperty(name="Widgets Alpha",
                                                    min=0.0, max=1.0, default=0.25,
                                                    subtype='PERCENTAGE')

    armature_type.pizmo_widget_scale = FloatProperty(name="Widgets Scale",
                                                     min=0.1, max=3.0, default=1.1,
                                                     update=wizmo.GrouzMo.mark_dirty
                                                     )


def register_properties():
    bpy.types.WindowManager.pizmo_display_widgets = bpy.props.BoolProperty(name="Display Pizmo",
                                                                           description="Geometry picker for armatures",
                                                                           default=True)

    register_bone_properties()
    register_armature_properties()


def unregister_properties():
    del bpy.types.WindowManager.pizmo_display_widgets

    del bpy.types.PoseBone.pizmo_vis_type
    del bpy.types.PoseBone.pizmo_vis_shape
    del bpy.types.PoseBone.pizmo_drag_action
    del bpy.types.PoseBone.pizmo_alt_drag_action
    del bpy.types.PoseBone.pizmo_shape_frame
    del bpy.types.PoseBone.pizmo_shape_scale
    del bpy.types.PoseBone.pizmo_shape_offset

    del bpy.types.PoseBone.pizmo_vis_mesh
    del bpy.types.PoseBone.pizmo_vert_grp
    del bpy.types.PoseBone.pizmo_min_vertweight

    del bpy.types.Armature.pizmo_armature_widget
    del bpy.types.Armature.pizmo_color_base
    del bpy.types.Armature.pizmo_color_highlight
    del bpy.types.Armature.pizmo_color_alpha
    del bpy.types.Armature.pizmo_color_selected
    del bpy.types.Armature.pizmo_widget_scale
    del bpy.types.Armature.pizmo_armature_root
