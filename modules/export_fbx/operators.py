# coding: utf-8
import bpy
import os
import subprocess
import math
from datetime import datetime

# Operator classes will be moved here
class MultiExport(bpy.types.Operator):
	"""Export FBXs/OBJs/GLTFs to Unity/UE/Godot"""
	bl_idname = "object.multi_export"
	bl_label = "Export FBXs/OBJs/GLTFs"
	bl_options = {'REGISTER', 'UNDO'}

	def execute(self, context):
		start_time = datetime.now()
		act = bpy.context.scene.act
		act.export_dir = ""
		incorrect_names = []

		# Check custom name
		if act.fbx_export_mode == 'ALL':
			if act.set_custom_fbx_name:
				if len(act.custom_fbx_name) == 0:
					from . import utils
					utils.show_message_box('Custom Name can\'t be empty',
							   'Saving Error',
							   'ERROR')
					return {'CANCELLED'}

		# Check saved blend file
		if len(bpy.data.filepath) == 0 and not act.custom_export_path:
			from . import utils
			utils.show_message_box('Blend file is not saved. Try use Custom Export Path',
					   'Saving Error',
					   'ERROR')
			return {'CANCELLED'}

		if len(bpy.data.filepath) > 0 or act.custom_export_path:
			path = ""

			# Check export path
			if len(bpy.data.filepath) > 0:
				if act.export_format == 'FBX':
					path = bpy.path.abspath('//FBXs/')
				if act.export_format == 'OBJ':
					path = bpy.path.abspath('//OBJs/')
				if act.export_format == 'GLTF':
					path = bpy.path.abspath('//GLTFs/')

			if act.custom_export_path:
				if len(act.export_path) == 0:
					from . import utils
					utils.show_message_box('Export Path can\'t be empty',
							   'Saving Error',
							   'ERROR')
					return {'CANCELLED'}

				if not os.path.exists(os.path.realpath(bpy.path.abspath(act.export_path))):
					from . import utils
					utils.show_message_box('Directory for export not exist',
							   'Saving Error',
							   'ERROR')
					return {'CANCELLED'}
				else:
					path = os.path.realpath(bpy.path.abspath(act.export_path)) + '/'

			# Create export folder (if this need)
			if not os.path.exists(path):
				os.makedirs(path)

			# Save selected objects and active object
			start_selected_obj = bpy.context.selected_objects
			start_active_obj = bpy.context.active_object
			current_selected_obj = bpy.context.selected_objects

			# Check "Pivot Point Align" option, save start state and disable it
			current_pivot_point_align = bpy.context.scene.tool_settings.use_transform_pivot_point_align
			if current_pivot_point_align:
				bpy.context.scene.tool_settings.use_transform_pivot_point_align = False

			# Save cursor location and pivot point mode
			saved_cursor_loc = bpy.context.scene.cursor.location.copy()
			current_pivot_point = bpy.context.scene.tool_settings.transform_pivot_point

			# Name for FBX is active object name (by default)
			name = bpy.context.active_object.name

			# Filtering selected objects. Exclude all not meshes, empties, armatures, curves and text
			bpy.ops.object.select_all(action='DESELECT')
			for x in current_selected_obj:
				if x.type == 'MESH' or x.type == 'EMPTY' or x.type == 'ARMATURE' or x.type == 'CURVE' or x.type == 'FONT':
					x.select_set(True)
			current_selected_obj = bpy.context.selected_objects

			# Added suffix _ex to all selected objects. Also add _ex to mesh data and armature name
			for obj in current_selected_obj:
				obj.name += "_ex"
				if obj.type == 'MESH' or obj.type == 'ARMATURE':
					obj.data.name += "_ex"

			# Make copies. These copies will be exported
			bpy.ops.object.duplicate()
			exp_objects = bpy.context.selected_objects

			if act.export_target_engine == 'UNITY2023' and act.export_format == 'FBX':
				if act.export_combine_meshes:
					bpy.ops.object.make_single_user(type='SELECTED_OBJECTS', object=True, obdata=True)
			else:
				bpy.ops.object.make_single_user(type='SELECTED_OBJECTS', object=True, obdata=True)

			# Convert all non-mesh objects to mesh (except empties)
			for obj in exp_objects:
				bpy.ops.object.select_all(action='DESELECT')
				obj.select_set(True)
				bpy.context.view_layer.objects.active = obj

				# Remove disabled modifiers
				if obj.type != 'EMPTY':
					for modifier in reversed(obj.modifiers):
						if not (modifier.show_viewport and modifier.show_render):
							obj.modifiers.remove(modifier)

				# Apply modifiers (except Armature)
				if act.export_target_engine == 'UNITY2023' and act.export_format == 'FBX':
					# Processing only objects without linked data or for all of enabled option combine meshes
					if ((obj.type == 'MESH' and obj.data.users < 2) or (
							act.fbx_export_mode != 'INDIVIDUAL' and act.export_combine_meshes)):
						for modifier in obj.modifiers:
							if modifier.type != 'ARMATURE':
								try:
									bpy.ops.object.modifier_apply(modifier=modifier.name)
								except:
									bpy.ops.object.modifier_remove(modifier=modifier.name)
					elif obj.type != 'EMPTY':
						bpy.ops.object.convert(target='MESH')
				else:
					if obj.type == 'MESH':
						for modifier in obj.modifiers:
							if modifier.type != 'ARMATURE':
								try:
									bpy.ops.object.modifier_apply(modifier=modifier.name)
								except:
									bpy.ops.object.modifier_remove(modifier=modifier.name)
					elif obj.type != 'EMPTY':
						bpy.ops.object.convert(target='MESH')
			# Delete _ex.001 suffix from object names.
			# Mesh name and armature name is object name
			for obj in exp_objects:
				obj.name = obj.name[:-7]
				if obj.type == 'MESH' or obj.type == 'ARMATURE':
					obj.data.name = obj.name

			# Delete all materials (Optional)
			if act.delete_mats_before_export:
				for o in exp_objects:
					if o.type == 'MESH' and len(o.data.materials) > 0:
						for q in reversed(range(len(o.data.materials))):
							bpy.context.object.active_material_index = q
							o.data.materials.pop(index=q)

			# Triangulate meshes (Optional)
			if act.triangulate_before_export:
				for o in exp_objects:
					if o.type == 'MESH':
						bpy.ops.object.select_all(action='DESELECT')
						o.select_set(True)
						bpy.context.view_layer.objects.active = o
						bpy.ops.object.mode_set(mode='EDIT')
						bpy.ops.mesh.reveal()
						bpy.ops.mesh.select_all(action='SELECT')
						bpy.ops.mesh.quads_convert_to_tris(quad_method='BEAUTY', ngon_method='BEAUTY')
						bpy.ops.mesh.select_all(action='DESELECT')
						bpy.ops.object.mode_set(mode='OBJECT')

			# Select all exported objects
			for obj in exp_objects:
				obj.select_set(True)

			# Apply Scale and Rotation for UNITY2023 Export or GLTF
			# Processing only objects without linked data
			if (act.export_target_engine == 'UNITY2023' and act.export_format == 'FBX') or act.export_format == 'GLTF':
				current_active = bpy.context.view_layer.objects.active
				bpy.ops.object.select_all(action='DESELECT')
				for x in exp_objects:
					if (x.type == 'MESH' and x.data.users < 2) or x.type != 'MESH':
						bpy.context.view_layer.objects.active = x
						x.select_set(True)
				bpy.ops.object.transform_apply(location=False, rotation=act.apply_rot, scale=act.apply_scale)
				bpy.context.view_layer.objects.active = current_active
			else:
				# Apply scale
				bpy.ops.object.transform_apply(location=False, rotation=False, scale=act.apply_scale)
				# Rotation Fix. Rotate X -90, Apply, Rotate X 90
				if act.apply_rot:
					bpy.context.scene.tool_settings.transform_pivot_point = 'MEDIAN_POINT'

					# Operate only with higher level parents
					for x in exp_objects:
						bpy.ops.object.select_all(action='DESELECT')

						if x.parent is None:
							x.select_set(True)
							bpy.context.view_layer.objects.active = x

							# Check object has any rotation
							# for option "Apply for Rotated Objects"
							child_rotated = False
							bpy.ops.object.select_grouped(extend=True, type='CHILDREN_RECURSIVE')
							for y in bpy.context.selected_objects:
								if abs(y.rotation_euler.x) + abs(y.rotation_euler.y) + abs(y.rotation_euler.z) > 0.017:
									child_rotated = True

							bpy.ops.object.select_all(action='DESELECT')
							x.select_set(True)

							# X-rotation fix
							if act.export_format == 'FBX' and (act.apply_rot_rotated
															   or (not act.apply_rot_rotated and not child_rotated)
															   or not act.fbx_export_mode == 'PARENT'):
								bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
								bpy.ops.transform.rotate(
									value=(math.pi * -90 / 180), orient_axis='X',
									orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)),
									orient_type='GLOBAL', constraint_axis=(True, False, False),
									orient_matrix_type='GLOBAL', mirror=False,
									use_proportional_edit=False, proportional_edit_falloff='SMOOTH',
									proportional_size=1)
								bpy.ops.object.select_grouped(extend=True, type='CHILDREN_RECURSIVE')
								bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
								bpy.ops.object.select_all(action='DESELECT')
								x.select_set(True)
								bpy.ops.transform.rotate(
									value=(math.pi * 90 / 180), orient_axis='X',
									orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)),
									orient_type='GLOBAL', constraint_axis=(True, False, False),
									orient_matrix_type='GLOBAL', mirror=False,
									use_proportional_edit=False, proportional_edit_falloff='SMOOTH',
									proportional_size=1)

			bpy.ops.object.select_all(action='DESELECT')

			# Select exported objects
			for x in exp_objects:
				if x.type == 'MESH' or x.type == 'EMPTY' or x.type == 'ARMATURE':
					x.select_set(True)

			# Store duplicated data for cleanUp
			duplicated_data = []
			for obj in exp_objects:
				if obj.type == 'MESH':
					duplicated_data.append(obj.data.name)

			# Export all as one fbx
			if act.fbx_export_mode == 'ALL':
				# Combine All Meshes (Optional)
				if act.export_combine_meshes:
					# If parent object is mesh
					# combine all children to parent object
					if start_active_obj.type == 'MESH':
						bpy.context.view_layer.objects.active = start_active_obj
						bpy.ops.object.join()
					# If  parent is empty
					else:
						current_active = bpy.context.view_layer.objects.active
						# Combine all child meshes to first in list
						for obj in exp_objects:
							if obj.type == 'MESH':
								bpy.context.view_layer.objects.active = obj
						bpy.ops.object.join()
						bpy.context.view_layer.objects.active = current_active

					exp_objects = bpy.context.selected_objects

				# Set custom fbx/obj name (Optional)
				if act.set_custom_fbx_name:
					prefilter_name = act.custom_fbx_name
				else:
					prefilter_name = name

				# Replace invalid chars
				name = utils.prefilter_export_name(prefilter_name)

				if name != prefilter_name:
					incorrect_names.append(prefilter_name)

				# Export FBX/OBJ/GLTF
				utils.export_model(path, name)

			# Individual Export
			if act.fbx_export_mode == 'INDIVIDUAL':
				for x in exp_objects:
					object_loc = (0.0, 0.0, 0.0)
					bpy.context.scene.tool_settings.transform_pivot_point = 'MEDIAN_POINT'
					# Select only current object
					bpy.ops.object.select_all(action='DESELECT')
					x.select_set(True)
					bpy.context.view_layer.objects.active = x

					# Apply Location - Center of fbx is origin of object (Optional)
					if act.apply_loc:
						# Copy object location
						bpy.ops.view3d.snap_cursor_to_selected()
						object_loc = bpy.context.scene.cursor.location.copy()
						# Move object to center of world
						bpy.ops.object.location_clear(clear_delta=False)
					# Center of fbx is center of the world
					else:
						bpy.ops.view3d.snap_cursor_to_center()
						bpy.context.scene.tool_settings.transform_pivot_point = 'CURSOR'
					prefilter_name = x.name

					# Replace invalid chars
					name = utils.prefilter_export_name(prefilter_name)

					if name != prefilter_name:
						incorrect_names.append(prefilter_name)

					# Export FBX/OBJ/GLTF
					utils.export_model(path, name)

					# Restore object location
					if act.apply_loc:
						bpy.context.scene.cursor.location = object_loc
						bpy.ops.view3d.snap_selected_to_cursor(use_offset=True)

			combined_meshes = []

			# Export by parents
			if act.fbx_export_mode == 'PARENT':
				bpy.ops.object.select_all(action='DESELECT')

				# Select only top level parents
				for x in exp_objects:
					if x.parent is None:
						x.select_set(True)

				parent_objs = bpy.context.selected_objects

				for x in parent_objs:
					bpy.ops.object.select_all(action='DESELECT')
					bpy.context.view_layer.objects.active = x
					x.select_set(True)
					# Combine All Meshes (Optional)
					if act.export_combine_meshes:
						# If parent object is mesh
						# combine all children to parent object
						if x.type == 'MESH':
							bpy.ops.object.select_grouped(extend=True, type='CHILDREN_RECURSIVE')
							bpy.ops.object.join()

							# CleanUp Empties without Children
							selected_objects_for_cleanup = bpy.context.selected_objects
							for obj in selected_objects_for_cleanup:
								if obj.type == "EMPTY" and len(obj.children) == 0:
									bpy.data.objects.remove(obj, do_unlink=True)

						# If  parent is not Mesh
						else:
							current_active = bpy.context.view_layer.objects.active
							parent_loc = current_active.location.copy()
							parent_name = current_active.name

							# Select all children
							bpy.ops.object.select_grouped(extend=False, type='CHILDREN_RECURSIVE')
							group_selected_objects = bpy.context.selected_objects

							# Combine all child meshes to first in list
							for obj in group_selected_objects:
								if obj.type == 'MESH':
									bpy.context.view_layer.objects.active = obj
							bpy.ops.object.join()

							bpy.context.view_layer.objects.active.name = parent_name + '_Mesh'

							# Parent Combined mesh back
							current_active.select_set(True)
							bpy.context.view_layer.objects.active = current_active
							bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)

							selected_objects_for_cleanup = bpy.context.selected_objects

							# Move Origin to Parent
							bpy.context.scene.tool_settings.transform_pivot_point = 'MEDIAN_POINT'
							bpy.context.scene.cursor.location = parent_loc
							bpy.ops.object.origin_set(type='ORIGIN_CURSOR', center='MEDIAN')

							# CleanUp Empties without Children
							for obj in selected_objects_for_cleanup:
								if obj.type == "EMPTY" and len(obj.children) == 0:
									bpy.data.objects.remove(obj, do_unlink=True)

							bpy.context.view_layer.objects.active = current_active

					current_parent = bpy.context.view_layer.objects.active

					object_loc = (0.0, 0.0, 0.0)
					bpy.context.scene.tool_settings.transform_pivot_point = 'MEDIAN_POINT'
					# Select only current object
					bpy.ops.object.select_all(action='DESELECT')

					current_parent.select_set(True)
					bpy.context.view_layer.objects.active = current_parent

					if act.apply_loc:
						# Copy object location
						bpy.ops.view3d.snap_cursor_to_selected()
						object_loc = bpy.context.scene.cursor.location.copy()
						# Move object to center
						bpy.ops.object.location_clear(clear_delta=False)
					else:
						bpy.ops.view3d.snap_cursor_to_center()
						bpy.context.scene.tool_settings.transform_pivot_point = 'CURSOR'

					# Name is name of parent
					prefilter_name = current_parent.name
					# Select Parent and his children
					bpy.ops.object.select_grouped(extend=True, type='CHILDREN_RECURSIVE')

					# Replace invalid chars
					name = utils.prefilter_export_name(prefilter_name)

					if name != prefilter_name:
						incorrect_names.append(prefilter_name)

					# Store objects after combine for future cleanup
					if act.export_combine_meshes:
						for obj in bpy.context.selected_objects:
							combined_meshes.append(obj)

					# Export FBX/OBJ/GLTF
					utils.export_model(path, name)
					bpy.ops.object.select_all(action='DESELECT')
					current_parent.select_set(True)

					# Restore object location
					if act.apply_loc:
						bpy.context.scene.cursor.location = object_loc
						bpy.ops.view3d.snap_selected_to_cursor(use_offset=True)

			# Export by collection
			if act.fbx_export_mode == 'COLLECTION':
				used_collections = []
				origin_loc = (0.0, 0.0, 0.0)
				bpy.context.scene.tool_settings.transform_pivot_point = 'MEDIAN_POINT'
				obj_col_dict = {}
				# Collect used collections for selected objects
				for x in exp_objects:
					collection_in_list = False

					for c in used_collections:
						if x.users_collection[0].name == c:
							collection_in_list = True

					if collection_in_list is False:
						used_collections.append(x.users_collection[0].name)

					obj_col_dict[x] = x.users_collection[0].name

				# Select objects by collection and export
				for c in used_collections:
					bpy.ops.object.select_all(action='DESELECT')

					# Select Objects in Collection
					set_active_mesh = False
					for obj, col_name in obj_col_dict.items():
						if col_name == c:
							obj.select_set(True)
							if obj.type == 'MESH' and not set_active_mesh:
								bpy.context.view_layer.objects.active = obj
								if act.export_combine_meshes:
									obj.name = c
								set_active_mesh = True

					if act.export_combine_meshes and set_active_mesh:
						bpy.ops.object.join()

						# Move Origin to Parent
						bpy.context.scene.cursor.location = origin_loc
						bpy.ops.object.origin_set(type='ORIGIN_CURSOR', center='MEDIAN')

						# CleanUp Empties without Children
						selected_objects_for_cleanup = bpy.context.selected_objects
						for obj in selected_objects_for_cleanup:
							if obj.type == "EMPTY" and len(obj.children) == 0:
								bpy.data.objects.remove(obj, do_unlink=True)

					# Replace invalid chars
					name = utils.prefilter_export_name(c)

					if name != c:
						incorrect_names.append(c)

					# Store objects after combine for future cleanup
					if act.export_combine_meshes:
						for obj in bpy.context.selected_objects:
							combined_meshes.append(obj)

					# Export FBX/OBJ/GLTF
					utils.export_model(path, name)

				bpy.ops.object.select_all(action='DESELECT')

			if act.export_combine_meshes and (act.fbx_export_mode == 'PARENT' or act.fbx_export_mode == 'COLLECTION'):
				exp_objects = combined_meshes

			bpy.ops.object.select_all(action='DESELECT')

			for obj in exp_objects:
				obj.select_set(True)

			# Delete duplicates and cleanup
			bpy.ops.object.delete()

			for data_name in duplicated_data:
				try:
					bpy.data.meshes.remove(bpy.data.meshes[data_name])
				except:
					continue

			# Select again original objects and set active object
			bpy.ops.object.select_all(action='DESELECT')

			# Restore names of objects (remove "_ex" from name)
			for j in current_selected_obj:
				j.name = j.name[:-3]
				if j.type == 'MESH' or j.type == 'ARMATURE':
					j.data.name = j.data.name[:-3]

			for i in start_selected_obj:
				i.select_set(True)

			bpy.context.view_layer.objects.active = start_active_obj

			# Restore "Pivot point align" option
			bpy.context.scene.tool_settings.use_transform_pivot_point_align = current_pivot_point_align

			# Restore cursor location and pivot point mode
			bpy.context.scene.cursor.location = saved_cursor_loc
			bpy.context.scene.tool_settings.transform_pivot_point = current_pivot_point

			# Save export dir path for option "Open export dir"
			act.export_dir = path

		# Show message about incorrect names
		if len(incorrect_names) > 0:
			from . import utils
			utils.show_message_box(
				"Object(s) has invalid characters in name. Some chars in export name have been replaced",
				"Incorrect Export Names")

		utils.print_execution_time("FBX/OBJ Export", start_time)
		return {'FINISHED'}

# Open Export Directory
class OpenExportDir(bpy.types.Operator):
	"""Open Export Directory in OS"""
	bl_idname = "object.open_export_dir"
	bl_label = "Open Export Directory in OS"
	bl_options = {'REGISTER', 'UNDO'}

	def execute(self, context):
		start_time = datetime.now()
		act = bpy.context.scene.act

		if not os.path.exists(os.path.realpath(bpy.path.abspath(act.export_dir))):
			act.export_dir = ""
			from . import utils
			utils.show_message_box('Directory not exist',
					   'Wrong Path',
					   'ERROR')
			return {'CANCELLED'}

		# Try open export dir in OS
		if len(act.export_dir) > 0:
			try:
				os.startfile(act.export_dir)
			except:
				subprocess.Popen(['xdg-open', act.export_dir])
		else:
			from . import utils
			utils.show_message_box('Export FBX\'s before',
					   'Info')
			return {'FINISHED'}

		utils.print_execution_time("Open Export Directory", start_time)
		return {'FINISHED'}

classes = (
    MultiExport,
    OpenExportDir,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)