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
        row.prop(pbone, 'pizmo_vis_shape')
        if pbone.pizmo_vis_shape:
            row = layout.row()
            row.prop_search(pbone, "pizmo_vert_grp", pbone.pizmo_vis_shape, "vertex_groups", text="Vertex Group")
