# coding: utf-8
import bpy

# Import Export UI Panel
class VIEW3D_PT_import_export_tools_panel(bpy.types.Panel):
    bl_label = "Export Tools"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "PopTools"

    @classmethod
    def poll(self, context):
        # If this panel not hidden in preferences
        try:
            preferences = bpy.context.preferences.addons[__package__].preferences
            return (context.object is not None and context.mode == 'OBJECT') and preferences.export_import_enable
        except KeyError:
            return False

    def draw(self, context):
        act = bpy.context.scene.act
        layout = self.layout

        if context.object is not None:
            if context.mode == 'OBJECT':
                # Export Mode
                row = layout.row(align=True)
                row.label(text="Export Mode:")
                row.prop(act, 'fbx_export_mode', expand=False)

                # Export Format (FBX or OBJ)
                row = layout.row(align=True)
                row.label(text="File Format:")
                row.prop(act, "export_format", expand=False)

                if act.export_format == 'FBX':
                    # Target Engine
                    row = layout.row(align=True)
                    row.label(text="Target Engine:")
                    row.prop(act, "export_target_engine", expand=False)

                if not (act.export_format == 'OBJ' and (
                        act.fbx_export_mode == 'ALL' or act.fbx_export_mode == 'COLLECTION')):
                    # Apply Transforms
                    box = layout.box()
                    row = box.row()
                    row.label(text="Apply:")

                    row = box.row(align=True)
                    if act.export_format == 'FBX' or act.export_format == 'GLTF':
                        if act.apply_rot:
                            row.prop(act, "apply_rot", text="Rotation", icon="CHECKBOX_HLT")
                        else:
                            row.prop(act, "apply_rot", text="Rotation", icon="CHECKBOX_DEHLT")
                        if act.apply_scale:
                            row.prop(act, "apply_scale", text="Scale", icon="CHECKBOX_HLT")
                        else:
                            row.prop(act, "apply_scale", text="Scale", icon="CHECKBOX_DEHLT")

                    if act.fbx_export_mode == 'INDIVIDUAL' or act.fbx_export_mode == 'PARENT':
                        if act.apply_loc:
                            row.prop(act, "apply_loc", text="Location", icon="CHECKBOX_HLT")
                        else:
                            row.prop(act, "apply_loc", text="Location", icon="CHECKBOX_DEHLT")

                    if act.export_format == 'FBX':
                        if act.apply_rot and act.fbx_export_mode == 'PARENT' and act.export_target_engine != 'UNITY2023':
                            row = box.row()
                            row.prop(act, "apply_rot_rotated")

                row = layout.row()
                row.prop(act, "delete_mats_before_export", text="Delete All Materials")

                if act.fbx_export_mode != 'INDIVIDUAL':
                    row = layout.row()
                    row.prop(act, "export_combine_meshes", text="Combine All Meshes")

                row = layout.row()
                row.prop(act, "triangulate_before_export", text="Triangulate Meshes")

                if act.fbx_export_mode == 'ALL':
                    box = layout.box()
                    row = box.row()
                    row.prop(act, "set_custom_fbx_name", text="Custom Name for File")
                    if act.set_custom_fbx_name:
                        row = box.row(align=True)
                        row.label(text="File Name:")
                        row.prop(act, "custom_fbx_name")

                # Custom Export Options
                box = layout.box()
                row = box.row()
                row.prop(act, "export_custom_options", text="Custom Export Options")
                if act.export_custom_options:
                    if act.export_format == 'FBX':
                        row = box.row(align=True)
                        row.label(text=" Smoothing")
                        row.prop(act, "export_smoothing", expand=False)

                        row = box.row(align=True)
                        row.label(text=" Loose Edges")
                        row.prop(act, "export_loose_edges", text="")

                        row = box.row(align=True)
                        row.label(text=" Tangent Space")
                        row.prop(act, "export_tangent_space", text="")

                        row = box.row(align=True)
                        row.label(text=" Only Deform Bones")
                        row.prop(act, "export_only_deform_bones", text="")

                        row = box.row(align=True)
                        row.label(text=" Add Leaf Bones")
                        row.prop(act, "export_add_leaf_bones", text="")

                        row = box.row(align=True)
                        row.label(text=" VC color space")
                        row.prop(act, "export_vc_color_space", expand=False)

                        row = box.row(align=True)
                        row.label(text=" Custom Props")
                        row.prop(act, "export_custom_props", text="")

                    if act.export_format == 'OBJ':
                        row = box.row(align=True)
                        row.label(text=" Separate By Mats")
                        row.prop(act, "obj_separate_by_materials", text="")

                        row = box.row(align=True)
                        row.label(text=" Smooth Groups")
                        row.prop(act, "obj_export_smooth_groups", text="")

                    if act.export_format == 'FBX' or act.export_format == 'OBJ':
                        row = box.row(align=True)
                        row.label(text="Use Custom Scale")
                        row.prop(act, "use_custom_export_scale", text="")
                        if act.use_custom_export_scale:
                            row = box.row(align=True)
                            row.prop(act, "custom_export_scale_value", text="Scale")
                        row = box.row(align=True)
                        row.label(text="Use Custom Axes")
                        row.prop(act, "use_custom_export_axes", text="")
                        if act.use_custom_export_axes:
                            row = box.row(align=True)
                            row.label(text=" Forward")
                            row.prop(act, "custom_export_forward_axis", expand=False)
                            row = box.row(align=True)
                            row.label(text=" Up")
                            row.prop(act, "custom_export_up_axis", expand=False)

                    if act.export_format == 'GLTF':
                        row = box.row(align=True)
                        row.label(text=" Pack Images")
                        row.prop(act, "gltf_export_image_format", text="")

                        row = box.row(align=True)
                        row.label(text=" Deform Bones Only")
                        row.prop(act, "gltf_export_deform_bones_only", text="")

                        row = box.row(align=True)
                        row.label(text=" Custom Properties")
                        row.prop(act, "gltf_export_custom_properties", text="")

                        row = box.row(align=True)
                        row.label(text=" Tangents")
                        row.prop(act, "gltf_export_tangents", text="")

                        row = box.row(align=True)
                        row.label(text=" Attributes")
                        row.prop(act, "gltf_export_attributes", text="")

                box = layout.box()
                row = box.row()
                row.prop(act, "custom_export_path", text="Custom Export Path")
                if act.custom_export_path:
                    row = box.row(align=True)
                    row.label(text="Export Path:")
                    row.prop(act, "export_path")

                row = layout.row()
                if act.export_format == 'FBX':
                    if act.export_target_engine == 'UNITY' or act.export_target_engine == 'UNITY2023':
                        row.operator("object.multi_export", text="Export FBX to Unity")
                    else:
                        row.operator("object.multi_export", text="Export FBX to Unreal")
                if act.export_format == 'OBJ':
                    row.operator("object.multi_export", text="Export OBJ")
                if act.export_format == 'GLTF':
                    row.operator("object.multi_export", text="Export GLTF")

                if len(act.export_dir) > 0:
                    row = layout.row()
                    row.operator("object.open_export_dir", text="Open Export Directory")

        else:
            row = layout.row()
            row.label(text=" ")

# Register/unregister classes
classes = (
    VIEW3D_PT_import_export_tools_panel,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)