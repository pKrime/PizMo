
import bpy
from bpy.types import (
    Gizmo,
    GizmoGroup,
)

from mathutils import Matrix, Vector

from . import shapes
from . import storage
from . import enum_types

from importlib import reload
reload(shapes)
reload(storage)
reload(enum_types)


from .shapes import Quad2D, Cross2D, MeshShape3D
from .enum_types import WidgetType, ShapeType

class BazeMo(Gizmo):
    base_color = 0.1, 0.1, 0.1
    base_highlight = 0.2, 0.5, 0.6

    def reset_color(self):
        self.color = self.base_color
        self.alpha = 0.25

        self.color_highlight = self.base_highlight
        self.alpha_highlight = 0.25


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

        self.use_draw_modal = True
        self.use_draw_scale = False
        self.use_draw_offset_scale = False

    def set_custom_shape(self, vertices):
        self.custom_shape = self.new_custom_shape('TRIS', vertices)

    def set_bone(self, bone):
        self.bone_name = bone.name

    def set_position(self, x, y):
        self.matrix_offset[0][3] = x
        self.matrix_offset[1][3] = y

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


class BonezMo3D(BazeMo):
    bl_idname = "VIEW3D_GT_pizmo_bone3d"

    __slots__ = (
        "custom_shape",
        "bone_name",
        "_init_mouse_x",
        "_init_mouse_y",
        "_obj"
    )

    def _update_offset_matrix(self):
        pass

    def draw(self, context):
        self.draw_custom_shape(self.custom_shape)

    def draw_select(self, context, select_id):
        self.draw_custom_shape(self.custom_shape, select_id=select_id)

    def setup(self):
        self.reset_color()

        self.use_draw_modal = True
        self.use_draw_scale = False
        self.use_draw_offset_scale = False

    def refresh_shape(self):
        if not self._obj:
            return

        vertices = MeshShape3D(self._obj,
                               scale=1.1, vertex_group=self._v_grp).vertices

        self.custom_shape = self.new_custom_shape('TRIS', vertices)

    def set_object(self, obj, v_grp=None):
        self._obj = obj
        self._v_grp = v_grp
        self.refresh_shape()

    def set_bone(self, bone):
        self.bone_name = bone.name

    def set_position(self, x, y):
        self.matrix_offset[0][3] = x
        self.matrix_offset[1][3] = y

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
            self.hide_select = True

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

    sel_color = 0.3, 0.6, 0.7
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
        mpr.use_draw_modal = True

    # def draw_prepare(self, context):
    #     """align gizmos with view"""
    #     view_matrix = context.area.spaces.active.region_3d.view_matrix.normalized()
    #     # view_matrix.translation = context.area.spaces.active.region_3d.view_location
    #     giz_matrix = Matrix()
    #     giz_matrix.translation = Vector([1/context.area.spaces.active.region_3d.view_distance, 0, 0]) @ view_matrix# @ context.area.spaces.active.region_3d.window_matrix
    #
    #     for gizmo in self.gizmos:
    #         gizmo.matrix_space = giz_matrix

    def import_storage(self, context, clear_storage=True):
        store = storage.Storage()

        for widget in store.widgets():
            mpr = None
            if widget.type == WidgetType.BONE:
                bone_name = widget.data['bone_name']
                if bone_name in self.bone_names:
                    continue
                print("shape is", widget.shape)
                if widget.shape == ShapeType.MESH3D:
                    print("using bonezmo3d")
                    mpr = self.gizmos.new(BonezMo3D.bl_idname)
                    try:
                        v_grp = widget.data['vertex_group']
                    except KeyError:
                        mpr.set_object(widget.data['object'])
                    else:
                        mpr.set_object(widget.data['object'], v_grp=v_grp)
                else:
                    mpr = self.gizmos.new(BonezMo.bl_idname)

                mpr.set_bone(context.object.pose.bones[bone_name])
            if mpr:
                if widget.shape == ShapeType.VERTICES:
                    mpr.set_custom_shape(widget.data['vertices'])
                elif widget.shape == ShapeType.MESH:
                    raise NotImplementedError

                mpr.set_position(widget.position[0], widget.position[1])

        if clear_storage:
            store.clear()

    def refresh(self, context):
        self.import_storage(context)

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
                gizmo.hide_select = False
            try:
                gizmo.refresh_shape()
            except AttributeError:
                pass