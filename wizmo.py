
import bpy
from bpy.types import (
    Gizmo,
    GizmoGroup,
)

from mathutils import Matrix

# Coordinates (each one is a triangle).


class Tris2D:
    vertices = [
        [0.0, 0.0],
        [0.0, 1.0],
        [1.0, 1.0],
    ]


class Quad2D:
    vertices = Tris2D.vertices + [Tris2D.vertices[-1],
                                  [Tris2D.vertices[-1][0], Tris2D.vertices[0][1]],
                                  Tris2D.vertices[0]]


class BonezMo(Gizmo):
    bl_idname = "VIEW3D_GT_pizmo_bone"

    base_color = 1.0, 0.0, 0.0

    __slots__ = (
        "custom_shape",
        "bone_name",
    )

    def _update_offset_matrix(self):
        pass

    def reset_color(self):
        self.color = self.base_color
        self.alpha = 0.1

    def draw(self, context):
        self.draw_custom_shape(self.custom_shape)

    def draw_select(self, context, select_id):
        self.draw_custom_shape(self.custom_shape, select_id=select_id)

    def select_refresh(self):
        print("sel refresh")

    def setup(self):
        self.reset_color()

        if not hasattr(self, "custom_shape"):
            self.custom_shape = self.new_custom_shape('TRIS', Quad2D.vertices)

        mat = Matrix((
            (1.0, 0.0, 0.0, 1.0),
            (0.0, 0.0, 1.0, 0.0),
            (0.0, 1.0, 0.0, 0.0),
            (0.0, 0.0, 0.0, 1.0)
        ))

        self.matrix_basis = mat

    def invoke(self, context, event):
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
        mpr = self.gizmos.new(BonezMo.bl_idname)
        mpr.bone_name = 'root_dup_1'

        mpr.color_highlight = 0.75, 0.75, 1.0
        mpr.alpha_highlight = 0.25

        mpr.use_draw_modal = True

    def refresh(self, context):
        sel_names = [bone.name for bone in context.selected_pose_bones]
        for gizmo in self.gizmos:
            if gizmo.bone_name in sel_names:
                gizmo.color = self.sel_color
                gizmo.alpha = 0.5
            else:
                gizmo.reset_color()

