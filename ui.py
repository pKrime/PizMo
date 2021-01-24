import bpy


class ARMATURE_PT_pizmo_properties(bpy.types.Panel):
    bl_label = "Pizmo Armature Display"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "data"

    @classmethod
    def poll(cls, context):
        if not context.object:
            return False
        return context.object.type == 'ARMATURE'

    def draw(self, context):
        layout = self.layout

        row = layout.row()
        row.prop(context.object.data, 'pizmo_armature_widget')

        row = layout.row()
        row.label(text="Widget Colors")

        row = layout.row()
        row.prop(context.object.data, 'pizmo_color_base')

        row = layout.row()
        row.prop(context.object.data, 'pizmo_color_highlight')

        row = layout.row()
        row.prop(context.object.data, 'pizmo_color_selected')

        row = layout.row()
        row.prop(context.object.data, 'pizmo_color_alpha')

        row = layout.row()
        row.prop(context.object.data, 'pizmo_widget_scale')


class BONE_PT_pizmo_properties(bpy.types.Panel):
    bl_label = "Pizmo Bone Display"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "bone"

    @classmethod
    def poll(cls, context):
        if not context.object:
            return False
        return context.object.type == 'ARMATURE' and context.active_pose_bone

    def draw(self, context):
        layout = self.layout
        pbone = context.active_pose_bone

        row = layout.row()
        row.prop(pbone, 'pizmo_vis_type')

        if pbone.pizmo_vis_type == 'mesh':
            row = layout.row()
            row.prop(pbone, 'pizmo_vis_mesh')

            row = layout.row()
            if pbone.pizmo_vis_mesh:
                row.prop_search(pbone, "pizmo_vert_grp", pbone.pizmo_vis_mesh, "vertex_groups", text="Vertex Group")
            else:
                row.prop(pbone, "pizmo_vert_grp")

            row = layout.row()
            row.prop(pbone, "pizmo_min_vertweight")

        elif pbone.pizmo_vis_type == 'shape':
            row = layout.row()
            row.prop(pbone, 'pizmo_vis_shape')
            row = layout.row()
            row.prop(pbone, 'pizmo_shape_frame')
            row = layout.row()
            row.prop(pbone, 'pizmo_bone_follow')
