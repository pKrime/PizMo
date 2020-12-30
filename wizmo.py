
import bpy
from bpy.types import (
    Gizmo,
    GizmoGroup,
)

from mathutils import Matrix
from copy import copy, deepcopy

# Coordinates (each one is a triangle).


class BasicShape:
    vertices = []

    def __init__(self, scale=1.0):
        # make vertices unique to instance
        self.vertices = deepcopy(self.vertices)
        self.scale(scale)

    def scale(self, factor):
        for verts in self.vertices:
            for i, co in enumerate(verts):
                verts[i] = co * factor


class Tris2D(BasicShape):
    vertices = [
        [0.0, 0.0],
        [0.0, 1.0],
        [1.0, 1.0],
    ]


class Quad2D(BasicShape):
    vertices = deepcopy(Tris2D.vertices) + [deepcopy(Tris2D.vertices[-1]),
                                            [deepcopy(Tris2D.vertices[-1][0]), deepcopy(Tris2D.vertices[0][1])],
                                            deepcopy(Tris2D.vertices[0])]


class Rect2D:
    vertices = [
        [-0.5, -1.0],
        [-0.5, 1.0],
        [0.5, 1.0],

        [0.5, 1.0],
        [0.5, -1.0],
        [-0.5, -1.0],
    ]


class Cross2D:
    vertices = deepcopy(Rect2D.vertices) + [
        [-1.0, -0.5],
        [-1.0, 0.5],
        [1.0, 0.5],

        [1.0, 0.5],
        [1.0, -0.5],
        [-1.0, -0.5],
    ]


class BazeMo(Gizmo):
    base_color = 0.3, 0.6, 0.7

    __slots__ = (
        "custom_shape",
    )

    def reset_color(self):
        self.color = self.base_color
        self.alpha = 0.25


class AddzMo(BazeMo):
    bl_idname = "VIEW3D_GT_pizmo_add"

    def draw(self, context):
        self.draw_custom_shape(self.custom_shape)

    def draw_select(self, context, select_id):
        self.draw_custom_shape(self.custom_shape, select_id=select_id)

    def select_refresh(self):
        print("sel refresh")

    def setup(self):
        self.base_color = 0.25, 0.5, 0.5
        self.reset_color()

        if not hasattr(self, "custom_shape"):
            self.custom_shape = self.new_custom_shape('TRIS', Cross2D.vertices)

        mat = Matrix((
            (1.0, 0.0, 0.0, 1.0),
            (0.0, 0.0, 1.0, 0.0),
            (0.0, 1.0, 0.0, 0.0),
            (0.0, 0.0, 0.0, 1.0)
        ))

        self.matrix_basis = mat
        self.scale_basis = 0.25

    def invoke(self, context, event):
        mpr = self.group.gizmos.new(BonezMo.bl_idname)
        mpr.set_bone(context.active_pose_bone)
        return {'RUNNING_MODAL'}

    def exit(self, context, cancel):
        context.area.header_text_set(None)

    def modal(self, context, event, tweak):
        return {'RUNNING_MODAL'}


class BonezMo(BazeMo):
    bl_idname = "VIEW3D_GT_pizmo_bone"

    __slots__ = (
        "custom_shape",
        "bone_name",
        "_init_mouse_x",
        "_init_mouse_y",
    )

    def _update_offset_matrix(self):
        pass

    def draw(self, context):
        self.draw_custom_shape(self.custom_shape)

    def draw_select(self, context, select_id):
        self.draw_custom_shape(self.custom_shape, select_id=select_id)

    def select_refresh(self):
        print("sel refresh")

    def setup(self):
        self.reset_color()

        if not hasattr(self, "custom_shape"):
            self.custom_shape = self.new_custom_shape('TRIS', Quad2D(scale=0.25).vertices)

        mat = Matrix((
            (1.0, 0.0, 0.0, 0.0),
            (0.0, 0.0, 1.0, 0.0),
            (0.0, 1.0, 0.0, 0.0),
            (0.0, 0.0, 0.0, 1.0)
        ))

        self.matrix_basis = mat
        self.use_draw_modal = True

    def set_bone(self, bone):
        self.bone_name = bone.name

        position = bone.head

        self.matrix_offset[0][3] = position.x + 2
        self.matrix_offset[1][3] = position.z

    def invoke(self, context, event):
        self._init_mouse_y = event.mouse_y
        self._init_mouse_x = event.mouse_x

        bpy.ops.pose.select_all(action='DESELECT')

        try:
            bone = context.object.data.bones[self.bone_name]
        except KeyError:
            pass
        else:
            bone.select = True

        return {'RUNNING_MODAL'}

    def exit(self, context, cancel):
        context.area.header_text_set(None)

    def modal(self, context, event, tweak):
        delta_y = (event.mouse_y - self._init_mouse_y) / 1000.0
        delta_x = (event.mouse_x - self._init_mouse_x) / 1000.0

        move_mode = event.alt
        scale_mode = event.shift

        if move_mode:
            self.matrix_offset[0][3] += delta_x
            self.matrix_offset[1][3] += delta_y
        if scale_mode:
            self.scale_basis += delta_x

        return {'RUNNING_MODAL'}


class GrouzMo(GizmoGroup):
    bl_idname = "OBJECT_GGT_pizmo_armature"
    bl_label = "Test Light Widget"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'WINDOW'
    bl_options = {'3D', 'PERSISTENT'}

    sel_color = 0.25, 0.25, 0.5

    @classmethod
    def poll(cls, context):
        ob = context.object
        if ob and ob.type == 'ARMATURE':
            return ob.mode == 'POSE'
        return False

    def setup(self, context):
        # Assign the 'offset' target property to the light energy.

        mpr = self.gizmos.new(AddzMo.bl_idname)
        # mpr = self.gizmos.new(BonezMo.bl_idname)
        # mpr.bone_name = 'root_dup_1'

        mpr.color_highlight = 0.75, 0.75, 1.0
        mpr.alpha_highlight = 0.25

        mpr.use_draw_modal = True

    def draw_prepare(self, context):
        view_matrix = context.area.spaces.active.region_3d.view_matrix.inverted().normalized()
        for gizmo in self.gizmos:
            view_matrix.translation = gizmo.matrix_basis.translation
            gizmo.matrix_basis = view_matrix

    def refresh(self, context):
        sel_names = [bone.name for bone in context.selected_pose_bones]
        for gizmo in self.gizmos:
            try:
                bone_name = gizmo.bone_name
            except AttributeError:
                continue
            if bone_name in sel_names:
                gizmo.color = self.sel_color
                gizmo.alpha = 0.5
            else:
                gizmo.reset_color()
