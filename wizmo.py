
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


from .shapes import Cross2D, MeshShape3D
from .enum_types import WidgetType, ShapeType

class BazeMo(Gizmo):
    base_color = 0.1, 0.1, 0.1
    base_highlight = 0.2, 0.5, 0.6

    def reset_color(self):
        self.color = self.base_color
        self.alpha = 0.25

        self.color_highlight = self.base_highlight
        self.alpha_highlight = 0.25


class ArmzMo(BazeMo):
    bl_idname = "VIEW3D_GT_pizmo_root"
    to_delete = False

    __slots__ = (
        "_custom_shape",
        "bone_name",
        "_object",
    )

    def refresh_shape(self):
        if bpy.context.mode == 'POSE':
            self.hide = self._object == bpy.context.object

            try:
                p_bone = self._object.pose.bones[self.bone_name]
            except ReferenceError:
                self.to_delete = True
            else:
                self.matrix_space = p_bone.matrix
        else:
            self.hide = not self._object.visible_get()

    def draw(self, context):
        self.draw_custom_shape(self.custom_shape)

    def draw_select(self, context, select_id):
        self.draw_custom_shape(self.custom_shape, select_id=select_id)

    def invoke(self, context, event):
        if self._object:
            bpy.ops.object.mode_set(mode='OBJECT')
            bpy.ops.object.select_all(action='DESELECT')
            try:
                self._object.select_set(True)
            except ReferenceError:
                self.to_delete = True
                return {'FINISHED'}

            bpy.context.view_layer.objects.active = self._object
            bpy.ops.object.mode_set(mode='POSE')
        return {'RUNNING_MODAL'}

    def modal(self, context, event, tweak):
        return {'FINISHED'}

    def setup(self):
        self.bone_name = ''
        self.base_color = 0.25, 0.5, 0.5
        self.reset_color()

        if not hasattr(self, "custom_shape"):
            self.custom_shape = self.new_custom_shape('TRIS', Cross2D.vertices)

        self.use_draw_modal = True
        self.use_draw_scale = False
        self.use_draw_offset_scale = False

    def set_object(self, obj):
        self._object = obj
        # TODO: pick lowest bone in separate func
        self.bone_name = next((bone.name for bone in obj.pose.bones if not bone.parent), None)


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
        "bone_follow"
    )

    def refresh_shape(self, context):
        if self.bone_follow:
            self.matrix_space = context.object.pose.bones[self.bone_name].matrix

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
        "_meshshape",
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

    def refresh_shape(self, context):
        if not self._meshshape:
            return

        self.custom_shape = self.new_custom_shape('TRIS', self._meshshape.vertices)

    def set_object(self, obj, v_grp=None):
        if v_grp:
            if '{side}' in v_grp:
                v_grps = [v_grp.replace('{side}', 'L'), v_grp.replace('{side}', 'R')]
            else:
                v_grps = [v_grp]
        else:
            v_grps = []

        self._meshshape = MeshShape3D(obj, scale=1.1, vertex_groups=v_grps)
        if len(self._meshshape.vertices) > 2:
            self.refresh_shape(None)

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


class GrouzMo2D(GizmoGroup):
    def __init__(self):
        raise NotImplementedError

    def draw_prepare(self, context):
        """align gizmos with view"""
        view_matrix = context.area.spaces.active.region_3d.view_matrix.normalized()
        # view_matrix.translation = context.area.spaces.active.region_3d.view_location
        giz_matrix = Matrix()
        giz_matrix.translation = Vector([1/context.area.spaces.active.region_3d.view_distance, 0, 0]) @ view_matrix# @ context.area.spaces.active.region_3d.window_matrix

        for gizmo in self.gizmos:
            gizmo.matrix_space = giz_matrix


class GrouzMo(GizmoGroup):
    bl_idname = "OBJECT_GGT_pizmo_armature"
    bl_label = "Test Light Widget"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'WINDOW'
    bl_options = {'3D', 'PERSISTENT'}

    sel_color = 0.3, 0.6, 0.7
    draw_offset = [0.0, 0.0]

    _object = None
    _dirty = False

    @classmethod
    def poll(cls, context):
        ob = context.object
        if ob and ob.type == 'ARMATURE':
            return ob.mode == 'POSE'
        return False

    @property
    def bone_names(self):
        return [gizmo.bone_name for gizmo in self.gizmos if hasattr(gizmo, 'bone_name')]

    def setup_from_bone_attrs(self, context):
        for bone in context.object.pose.bones:
            if bone.pizmo_vis_type == 'mesh' and bone.pizmo_vis_mesh:
                mpr = self.gizmos.new(BonezMo3D.bl_idname)
                mpr.set_object(bone.pizmo_vis_mesh, v_grp=bone.pizmo_vert_grp)
                mpr.set_bone(bone)
            elif bone.pizmo_vis_type == 'shape' and bone.pizmo_vis_shape != 'none':
                if bone.pizmo_vis_shape == 'quad':
                    wdg_shape = shapes.Quad2D()
                else:
                    # TODO: report warning
                    print("coudl not generate shape", bone.pizmo_vis_shape, "for", bone.name)
                    continue

                wdg_shape.center()
                wdg_verts = wdg_shape.frame_vertices() if bone.pizmo_shape_frame else wdg_shape.vertices
                mpr = self.gizmos.new(BonezMo.bl_idname)
                mpr.set_custom_shape(wdg_verts)
                mpr.bone_follow = bone.pizmo_bone_follow
                mpr.set_bone(bone)

        self._object = context.object

    def setup(self, context):
        if context.object:
            self.setup_from_bone_attrs(context)

    def tallest_rigged_mesh(self, context):
        rigged_objs = list(
            (ob for ob in bpy.data.objects if ob.type == 'MESH'
             and next((mod for mod in ob.modifiers if mod.type == 'ARMATURE' and mod.object == context.object), None))
        )

        if not rigged_objs:
            return

        max_height = max(ob.dimensions[2] for ob in rigged_objs)
        tallest = next(ob for ob in rigged_objs if ob.dimensions[2] == max_height)
        return tallest

    def import_storage(self, context, clear_storage=False):
        store = storage.Storage()
        tallest = self.tallest_rigged_mesh(context)

        for widget in store.widgets():
            mpr = None
            if widget.type == WidgetType.BONE:
                bone_name = widget.data['bone_name']
                if bone_name not in context.object.pose.bones:
                    continue
                if bone_name in self.bone_names:
                    continue

                if widget.shape == ShapeType.MESH3D:
                    mpr = self.gizmos.new(BonezMo3D.bl_idname)
                    v_grp = widget.data.get('vertex_group')
                    mesh_obj = widget.data.get('object', tallest)
                    mpr.set_object(mesh_obj, v_grp=v_grp)
                elif widget.shape == ShapeType.RECT:
                    mpr = self.gizmos.new(BonezMo.bl_idname)
                    mpr.set_custom_shape(shapes.Rect2D.vertices)
                elif widget.shape == ShapeType.QUAD:
                    mpr = self.gizmos.new(BonezMo.bl_idname)
                    if widget.data.get('frame'):
                        mpr.set_custom_shape(shapes.Quad2D().frame_vertices())
                    else:
                        mpr.set_custom_shape(shapes.Quad2D.vertices)
                    if widget.data.get('bone_follow'):
                        mpr.bone_follow = True
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

    def clear(self):
        for gizmo in reversed(self.gizmos):
            self.gizmos.remove(gizmo)

    @staticmethod
    def mark_dirty(actor, context):
        GrouzMo._dirty = True

    def refresh(self, context):
        if context.object != self._object:
            GrouzMo._dirty = True

        if GrouzMo._dirty:
            self.clear()

        if not self.gizmos:
            self.setup_from_bone_attrs(context)

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
                gizmo.refresh_shape(context)
            except AttributeError:
                pass

        GrouzMo._dirty = False


class GrouzMoRoots(GizmoGroup):
    bl_idname = "OBJECT_GGT_pizmo_roots"
    bl_label = "Selects Armature"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'WINDOW'
    bl_options = {'3D', 'PERSISTENT'}

    sel_color = 0.3, 0.6, 0.7
    draw_offset = [0.0, 0.0]

    @classmethod
    def poll(cls, context):
        return context.mode in ('OBJECT', 'POSE')

    def setup(self, context):
        for ob in context.scene.objects:
            if not ob.visible_get():
                continue
            if ob.type != 'ARMATURE':
                continue
            mpr = self.gizmos.new(ArmzMo.bl_idname)
            mpr.set_object(ob)

    def refresh(self, context):
        for gizmo in reversed(self.gizmos):
            gizmo.refresh_shape()

            if gizmo.to_delete:
                self.gizmos.remove(gizmo)

