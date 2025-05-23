# panels.py
""" 
EasyMesh Batch Exporter UI Panels
This module contains the UI panels for the EasyMesh Batch Exporter add-on. 
It includes the main exporter panel, LOD settings, and recent exports
"""

import bpy
import time
import logging
import os
from bpy.types import Panel
from . import export_indicators

# --- Setup Logger ---
logger = logging.getLogger(__name__)
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter("%(name)s:%(levelname)s: %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)  # Default level

# Main UI Panel
class MESH_PT_exporter_panel(Panel):
    bl_label = "EasyMesh Batch Exporter"
    bl_idname = "MESH_PT_exporter_panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "PopTools" # Match bl_info location
    bl_order = 3

    # Helper functions
    def format_has_scale(self, format):
        """Check if the format is compatible with scale export setting"""
        return format in {"FBX", "OBJ", "STL"}

    def format_has_coordinates(self, format):
        """Check if the format is compatible with coordinate export settings"""
        return format in {"FBX", "OBJ", "USD", "STL"}
    
    def format_has_smoothing(self, format):
        """Check if the format is compatible with smoothing export settings"""
        return format in {"FBX"}


    def draw(self, context):
        layout = self.layout

        # --- Debugging Start ---
        # logger.info("--- Drawing MESH_PT_exporter_panel ---")
        if not hasattr(context.scene, "mesh_exporter"):
            logger.error("context.scene has no 'mesh_exporter' attribute!")
            layout.label(text="Error: Property group not registered?")
            return # Stop drawing if the group isn't there
        
        settings = context.scene.mesh_exporter

        if settings is None:
            logger.error("context.scene.mesh_exporter is None!")
            layout.label(text="Error: Property group is None?")
            return # Stop drawing if the group is None
        
        # logger.info(f"Settings object: {settings}")
        # try:
            # Try accessing a property directly
            # path_value = settings.mesh_export_path
            # logger.info(f"Value of mesh_export_path: {path_value}")
        # except AttributeError:
        #     logger.error("Could not access settings.mesh_export_path!")
        # --- Debugging End ---

        layout.use_property_split = True
        layout.use_property_decorate = False

        # Export path settings
        layout.prop(settings, "mesh_export_path")
        layout.prop(settings, "mesh_export_format")

        # Format-specific settings
        if settings.mesh_export_format == "GLTF":
            # GLTF-specific settings
            col = layout.column(heading="GLTF Type", align=True)
            row = col.row(align=True)
            row.prop(settings, "mesh_export_gltf_type", expand=True)

            col = layout.column(heading="Materials", align=True)
            row = col.row(align=True)
            row.prop(settings, "mesh_export_gltf_materials")

        # Coordinate system settings
        if self.format_has_coordinates(settings.mesh_export_format):
            col = layout.column(heading="Coordinate system", align=True)
            row = col.row(align=True)
            row.prop(settings, "mesh_export_coord_up", expand=True)
            row = col.row(align=True)
            row.prop(settings, "mesh_export_coord_forward", expand=True)

        # Scale settings
        if self.format_has_scale(settings.mesh_export_format):
            col = layout.column(heading="Scale", align=True)
            col.prop(settings, "mesh_export_scale")

        # Units settings
        if self.format_has_scale(settings.mesh_export_format):
            col = layout.column(heading="Units", align=True)
            row = col.row(align=True)
            row.prop(settings, "mesh_export_units", expand=True)

        # Smoothing settings
        if self.format_has_smoothing(settings.mesh_export_format):
            # Only show if the format supports smoothing
            col = layout.column(heading="Smoothing", align=True)
            row = col.row(align=True)
            row.prop(settings, "mesh_export_smoothing", expand=True)

        # Zero location settings
        col = layout.column(heading="Transform", align=True)
        col.prop(settings, "mesh_export_zero_location")


        # Triangulate settings
        col = layout.column(heading="Triangulate", align=True)
        row = col.row(align=True)
        row.prop(settings, "mesh_export_tri", text="")
        sub = row.row(align=True)
        sub.enabled = settings.mesh_export_tri # Enable/disable sub-option
        sub.prop(settings, "mesh_export_tri_method", text="")
        row = col.row(align=True)
        row.enabled = settings.mesh_export_tri # Enable/disable sub-option
        row.prop(settings, "mesh_export_keep_normals")

        # Rename file settings
        col = layout.column(heading="Rename file", align=True)
        col.prop(settings, "mesh_export_prefix")
        col.prop(settings, "mesh_export_suffix")

        layout.separator()

        # Materials export option
        col = layout.column(heading="Materials", align=True)
        col.prop(settings, "mesh_export_materials")
        
        # Export Button 
        mesh_count = sum(
            1 for obj in context.selected_objects if obj.type == "MESH"
        )
        # col = layout.column(heading="Export Control", align=True)
        # box = col.box()
        # row = box.row()
        # row.label(text=f"Selected Meshes: {mesh_count}", icon="MESH_DATA")
        # Export button (always enabled unless poll() fails)
        row = layout.row()
        # Generate the button text first
        button_text = (
            f"Export Meshes ({mesh_count})" if mesh_count > 0 
            else "Export Meshes")
        # Pass the generated text to the "text" parameter
        row.operator("mesh.batch_export", text=button_text, icon="EXPORT")
        
        # Open Export Directory button
        export_path = bpy.path.abspath(settings.mesh_export_path)
        if os.path.exists(export_path):
            row = layout.row()
            row.operator("mesh.open_export_directory", text="打开导出目录", icon="FILEBROWSER")


# LOD Panel
class MESH_PT_exporter_panel_lod(Panel):
    bl_label = "Quick LODs"
    bl_idname = "MESH_PT_exporter_panel_lod"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI" 
    bl_category = "Exporter" 
    bl_parent_id = "MESH_PT_exporter_panel" 
    bl_options = {"DEFAULT_CLOSED"} # Optional: Start closed

    @classmethod
    def poll(cls, context):
        # Show only if the main panel exists and path is set
        settings = context.scene.mesh_exporter
        # Check if the path property itself exists and is not None/empty
        return (settings 
                and settings.mesh_export_path 
                is not None 
                and settings.mesh_export_path != "")

    def draw_header(self, context):
        layout = self.layout
        settings = context.scene.mesh_exporter
        layout.prop(settings, "mesh_export_lod", text="") # Checkbox in header

    def draw(self, context):
        layout = self.layout
        settings = context.scene.mesh_exporter

        layout.use_property_split = True
        layout.use_property_decorate = False

        # Enable/disable based on the header checkbox
        layout.enabled = settings.mesh_export_lod

        col = layout.column(heading="Symmetry", align=True)
        row = col.row(align=True)
        # Add the symmetry checkbox to the row
        row.prop(settings, "mesh_export_lod_symmetry", text="")
        # Create a sub-row for the axis enum that can be disabled
        sub = row.row(align=True)
        # Disable the sub-row (and its contents) if symmetry is off
        sub.enabled = settings.mesh_export_lod_symmetry
        # Add the axis enum property to the sub-row
        sub.prop(settings, "mesh_export_lod_symmetry_axis", expand=True)

        col = layout.column(align=True)
        col.prop(settings, "mesh_export_lod_count")
        # Hide the decimate type bc I'm not sure if it's needed yet
        # col.prop(settings, "mesh_export_lod_type")

        box = layout.box()
        col = box.column(align=True)
        # col.label(text="Ratios:")
        # Display relevant properties based on type
        if settings.mesh_export_lod_type == "COLLAPSE":
            row = col.row(align=True)
            row.prop(settings, "mesh_export_lod_ratio_01", text="LOD1")
            row = col.row(align=True)
            row.prop(settings, "mesh_export_lod_ratio_02", text="LOD2")
            if settings.mesh_export_lod_count < 2:
                # Visual indicator for which LODs are disabled
                row.enabled = False
            row = col.row(align=True)
            row.prop(settings, "mesh_export_lod_ratio_03", text="LOD3")
            if settings.mesh_export_lod_count < 3:
                # Visual indicator for which LODs are disabled
                row.enabled = False
            row = col.row(align=True)
            row.prop(settings, "mesh_export_lod_ratio_04", text="LOD4")
            if settings.mesh_export_lod_count < 4:
                # Visual indicator for which LODs are disabled
                row.enabled = False
        elif settings.mesh_export_lod_type == "UNSUBDIVIDE":
            # Unsudivide should use Int for iterations
            # Can fix this later if needed
            col.prop(settings, "mesh_export_lod_ratio_01", text="LOD1 Iter.")
            col.prop(settings, "mesh_export_lod_ratio_02", text="LOD2 Iter.")
            col.prop(settings, "mesh_export_lod_ratio_03", text="LOD3 Iter.")
            col.prop(settings, "mesh_export_lod_ratio_04", text="LOD4 Iter.")


# Recent Exports Panel
class MESH_EXPORT_PT_recent_exports(Panel):
    bl_label = "Recent Exports"
    bl_idname = "MESH_EXPORT_PT_recent_exports"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Exporter"
    bl_parent_id = "MESH_PT_exporter_panel"
    bl_options = {"DEFAULT_CLOSED"} # Optional: Start closed

    @classmethod
    def poll(cls, context):
        # Check if the indicator system is running and has data
        return hasattr(export_indicators, "get_recently_exported_objects")

    def draw(self, context):
        layout = self.layout

        try:
            # Use the function from the export_indicators module
            recently_exported = (
                export_indicators.get_recently_exported_objects()
            )
        except AttributeError:
            layout.label(text="Indicator system not fully loaded.")
            return

        if not recently_exported:
            layout.label(text="No recent mesh exports.")
            return

        # Keep as single combined list for now
        # Can separate into fresh/stale based on status if needed
        box = layout.box()
        col = box.column(align=True)

        max_items = 10 # Limit display length
        for i, (obj, export_time) in enumerate(recently_exported):
            if i >= max_items:
                row = col.row()
                row.label(text=f"... and "
                          f"{len(recently_exported) - max_items} more")
                break

            if not obj: 
                continue # Skip if object deleted

            row = col.row(align=True)
            icon = "HIDE_OFF" # Default icon

            # Button to select object
            # Get the operator instance
            op = row.operator(
                "object.select_by_name", 
                text="", 
                icon=icon
            )
            # Set the property on the returned operator instance
            op.object_name = obj.name 

            row.label(text=obj.name)

            # Time since export
            time_diff = time.time() - export_time
            if time_diff < 60:
                time_str = f"{int(time_diff)}s ago"
            elif time_diff < 3600:
                time_str = f"{int(time_diff/60)}m ago"
            else:
                time_str = f"{int(time_diff/3600)}h ago"
            row.label(text=time_str)

        # Clear Indicators button if indicators are present
        if hasattr(export_indicators, "MESH_OT_clear_all_indicators"):
            layout.operator(
                export_indicators.MESH_OT_clear_all_indicators.bl_idname, 
                icon="TRASH"
            )



# Registration
classes = (
    MESH_PT_exporter_panel,
    MESH_PT_exporter_panel_lod,
    MESH_EXPORT_PT_recent_exports,
)

# register/unregister functions handled by __init__.py