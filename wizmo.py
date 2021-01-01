
import bpy
from bpy.types import (
    Gizmo,
    GizmoGroup,
)

from . import shapes

from importlib import reload
reload(shapes)

from .shapes import Quad2D, Cross2D


class BazeMo(Gizmo):
    base_color = 0.3, 0.6, 0.7

    def reset_color(self):
        self.color = self.base_color
        self.alpha = 0.25


class AddzMo(BazeMo):
    bl_idname = "VIEW3D_GT_pizmo_add"

    __slots__ = (
        "custom_shape",
        "_init_mouse_x",
        "_init_mouse_y",
    )

    def draw(self, context):
        self.draw_custom_shape(self.custom_shape)

    def draw_select(self, context, select_id):
        self.draw_custom_shape(self.custom_shape, select_id=select_id)

    def setup(self):
        self.base_color = 0.25, 0.5, 0.5
        self.reset_color()

        if not hasattr(self, "custom_shape"):
            self.custom_shape = self.new_custom_shape('TRIS', Cross2D.vertices)

        self.scale_basis = 0.25
        self.use_draw_modal = True
        self.use_draw_offset_scale = True

    def invoke(self, context, event):
        self._init_mouse_x = event.mouse_x
        self._init_mouse_y = event.mouse_y

        for bone in context.selected_pose_bones:
            if bone.name not in self.group.bone_names:
                mpr = self.group.gizmos.new(BonezMo.bl_idname)
                mpr.set_bone(bone)
        return {'RUNNING_MODAL'}

    def exit(self, context, cancel):
        context.area.header_text_set(None)

    def modal(self, context, event, tweak):
        delta_x = (event.mouse_x - self._init_mouse_x) / 1000.0
        delta_y = (event.mouse_y - self._init_mouse_y) / 1000.0

        for gizmo in self.group.gizmos:
            gizmo.matrix_offset[0][3] += delta_x
            gizmo.matrix_offset[2][3] += delta_y

        self.group.refresh(context)
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

    def setup(self):
        self.reset_color()

        if not hasattr(self, "custom_shape"):
            self.custom_shape = self.new_custom_shape('TRIS', Quad2D(scale=0.25).vertices)

        self.use_draw_modal = True
        self.use_draw_scale = True
        self.use_draw_offset_scale = True

    def set_bone(self, bone):
        self.bone_name = bone.name

        position = bone.head

        self.matrix_offset[0][3] = position.x + 2
        self.matrix_offset[1][3] = position.z

    def invoke(self, context, event):
        self._init_mouse_y = event.mouse_y
        self._init_mouse_x = event.mouse_x

        if not event.shift:
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
    draw_offset = [0.0, 0.0]

    @classmethod
    def poll(cls, context):
        ob = context.object
        if ob and ob.type == 'ARMATURE':
            return ob.mode == 'POSE'
        return False

    @property
    def bone_names(self):
        return [gizmo.bone_name for gizmo in self.gizmos if hasattr(gizmo, 'bone_name')]

    def setup(self, context):
        mpr = self.gizmos.new(AddzMo.bl_idname)

        mpr.color_highlight = 0.75, 0.75, 1.0
        mpr.alpha_highlight = 0.25

        mpr.use_draw_modal = True

    def draw_prepare(self, context):
        """align gizmos with view"""
        view_matrix = context.area.spaces.active.region_3d.view_matrix.inverted()
        view_matrix.translation = context.area.spaces.active.region_3d.view_location

        for gizmo in self.gizmos:
            gizmo.matrix_space = view_matrix

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
