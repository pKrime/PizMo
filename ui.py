import bpy


class BONE_PT_pizmo_buttons(bpy.types.Panel):
    bl_label = "Pizmo Display"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "bone"
    #bl_options = {'DEFAULT_OPEN'}

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

            # TODO: vertex_group threshold
        elif pbone.pizmo_vis_type == 'shape':
            row = layout.row()
            row.prop(pbone, 'pizmo_vis_shape')
            row = layout.row()
            row.prop(pbone, 'pizmo_shape_frame')
            row = layout.row()
            row.prop(pbone, 'pizmo_bone_follow')
