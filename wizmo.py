
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


from .shapes import Circle2D, Cross2D, MeshShape3D
from .enum_types import WidgetType, ShapeType


class BazeMo(Gizmo):

    def refresh_color(self, context=None, selected=False):
        context = context if context else bpy.context
        obj = context.object

        if obj and obj.type == 'ARMATURE':
            if selected:
                color = context.object.data.pizmo_color_selected
                alpha = min(obj.data.pizmo_color_alpha + 0.25, 1.0)
            else:
                color = obj.data.pizmo_color_base
                alpha = obj.data.pizmo_color_alpha
            color_highlight = obj.data.pizmo_color_highlight
        else:
            color = bpy.types.Armature.pizmo_color_base[1]['default']
            color_highlight = bpy.types.Armature.pizmo_color_highlight[1]['default']
            alpha = bpy.types.Armature.pizmo_color_alpha[1]['default']

        self.color = color
        self.color_highlight = color_highlight
        self.alpha = alpha
        self.alpha_highlight = self.alpha
        self.hide_selected = selected


class ArmzMo(BazeMo):
    bl_idname = "VIEW3D_GT_pizmo_root"
    to_delete = False

    __slots__ = (
        "_custom_shape",
        "bone_name",
        "_object",
    )

    def refresh_shape(self):
        # show armature select widget for all other armatures when in pose mode, all armatures when in object mode
        if bpy.context.mode == 'POSE':
            self.hide = self._object == bpy.context.object

            p_bone = self._object.pose.bones[self.bone_name]
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
        self.refresh_color()

        if not hasattr(self, "custom_shape"):
            self.custom_shape = self.new_custom_shape('TRIS', Circle2D().vertices)

        self.use_draw_modal = True
        self.use_draw_scale = False
        self.use_draw_offset_scale = False

    def set_object(self, obj, bone_name=""):
        self._object = obj

        if bone_name:
            self.bone_name = bone_name
        else:
            # TODO: pick lowest bone in separate func
            self.bone_name = next((bone.name for bone in obj.pose.bones if not bone.parent), None)


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
        self.refresh_color()

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
        "_meshshape",
    )

    def draw(self, context):
        self.draw_custom_shape(self.custom_shape)

    def draw_select(self, context, select_id):
        self.draw_custom_shape(self.custom_shape, select_id=select_id)

    def bone_is_visible(self, context):
        bone = context.object.data.bones[self.bone_name]
        layers = [i for i, layer in enumerate(bone.layers) if layer]

        return any([context.object.data.layers[i] for i in layers])

    def setup(self):
        self.refresh_color()

        self.use_draw_modal = True
        self.use_draw_scale = False
        self.use_draw_offset_scale = False

    def refresh_shape(self, context):
        if not self._meshshape:
            return

        if context:
            self.hide = not self.bone_is_visible(context)

        if not self.hide:
            self.custom_shape = self.new_custom_shape('TRIS', self._meshshape.vertices)

    def set_object(self, obj, v_grp=None, weight_threshold=0.2, widget_scale=1.1):
        if v_grp:
            if '{side}' in v_grp:
                v_grps = [v_grp.replace('{side}', 'L'), v_grp.replace('{side}', 'R')]
            else:
                v_grps = [v_grp]
        else:
            v_grps = []

        self._meshshape = MeshShape3D(obj, scale=widget_scale, vertex_groups=v_grps, weight_threshold=weight_threshold)
        if len(self._meshshape.vertices) > 2:
            self.refresh_shape(None)

    def set_bone(self, bone):
        self.bone_name = bone.name

    def set_position(self, x, y):
        self.matrix_offset[0][3] = x
        self.matrix_offset[1][3] = y

    def invoke(self, context, event):
        if not event.shift:
            bpy.ops.pose.select_all(action='DESELECT')

        try:
            bone = context.object.data.bones[self.bone_name]
        except KeyError:
            return {'FINISHED'}

        bone.select = True
        bones = context.object.data.bones
        bones.active = bones[bone.name]

        return {'RUNNING_MODAL'}

    def exit(self, context, cancel):
        context.area.header_text_set(None)

    def modal(self, context, event, tweak):
        return {'FINISHED'}


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
                mpr.set_object(bone.pizmo_vis_mesh, v_grp=bone.pizmo_vert_grp,
                               weight_threshold=bone.pizmo_min_vertweight,
                               widget_scale=context.object.data.pizmo_widget_scale)
                mpr.set_bone(bone)
            elif bone.pizmo_vis_type == 'shape' and bone.pizmo_vis_shape != 'none':
                if bone.pizmo_vis_shape == 'quad':
                    wdg_shape = shapes.Quad2D()
                elif bone.pizmo_vis_shape == 'circle':
                    wdg_shape = shapes.Circle2D()
                else:
                    # TODO: report warning
                    print("coudl not generate shape", bone.pizmo_vis_shape, "for", bone.name)
                    continue

                wdg_verts = wdg_shape.frame_vertices() if bone.pizmo_shape_frame else wdg_shape.vertices
                mpr = self.gizmos.new(BonezMo.bl_idname)
                mpr.set_custom_shape(wdg_verts)
                mpr.bone_follow = bone.pizmo_bone_follow
                mpr.set_bone(bone)

        self._object = context.object

    def setup(self, context):
        if context.object:
            self.setup_from_bone_attrs(context)

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
            gizmo.refresh_color(context, gizmo.bone_name in sel_names)
            gizmo.refresh_shape(context)

        GrouzMo._dirty = False


class GrouzMoRoots(GizmoGroup):
    bl_idname = "OBJECT_GGT_pizmo_roots"
    bl_label = "Selects Armature"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'WINDOW'
    bl_options = {'3D', 'PERSISTENT'}

    draw_offset = [0.0, 0.0]
    _dirty = False

    @classmethod
    def poll(cls, context):
        return context.mode in ('OBJECT', 'POSE')

    def setup(self, context):
        for ob in context.scene.objects:
            if not ob.visible_get():
                continue
            if ob.type != 'ARMATURE':
                continue
            if not ob.data.pizmo_armature_widget:
                continue

            mpr = self.gizmos.new(ArmzMo.bl_idname)
            mpr.set_object(ob)

    def refresh(self, context):
        if GrouzMoRoots._dirty:
            self.clear()
            self.setup(context)
            GrouzMoRoots._dirty = False

        for gizmo in reversed(self.gizmos):
            gizmo.refresh_shape()

    def clear(self):
        for gizmo in reversed(self.gizmos):
            self.gizmos.remove(gizmo)

    @staticmethod
    def mark_dirty(actor, context):
        GrouzMoRoots._dirty = True