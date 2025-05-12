# -*- coding: utf-8 -*-
"""
包含PopTools插件中网格导出器的Blender操作符。
处理选定网格对象的批量导出，包括LOD生成、
纹理压缩和临时对象的清理。
"""

import bpy
import os
import time
import contextlib
import re
import math
import logging
from bpy.types import Operator
from bpy.props import StringProperty
from . import indicators

# --- 设置日志记录器 ---
logger = logging.getLogger(__name__)
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter("%(name)s:%(levelname)s: %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)  # 默认级别

# --- 常量 ---
EXPORT_TIME_PROP = "mesh_export_timestamp"
EXPORT_STATUS_PROP = "mesh_export_status"


# --- 核心函数 ---


@contextlib.contextmanager
def temp_selection_context(context, active_object=None, selected_objects=None):
    """
    使用直接API临时设置活动对象和选择。
    
    参数:
        context (bpy.context): 当前Blender上下文。
        active_object (bpy.types.Object, optional): 
            要设置为活动的对象。
        selected_objects (list, optional): 要选择的对象列表。
    
    返回:
        None
    """
    # 存储原始状态
    original_active = context.view_layer.objects.active
    original_selected = [obj for obj in context.scene.objects 
                         if obj.select_get()]
    
    try:
        # 直接取消选择所有对象
        for obj in context.scene.objects:
            if obj.select_get():
                obj.select_set(False)
        
        # 直接选择请求的对象
        if selected_objects:
            if not isinstance(selected_objects, list):
                selected_objects = [selected_objects]
            
            for obj in selected_objects:
                if obj and obj.name in context.scene.objects:
                    try:
                        obj.select_set(True)
                    except ReferenceError:
                        logger.warning(f"无法选择'{obj.name}' "
                                       f"- 对象引用无效。")
        
        # 直接设置活动对象
        if active_object and active_object.name in context.scene.objects:
            context.view_layer.objects.active = active_object
        elif selected_objects:
            for obj in selected_objects:
                if obj and obj.name in context.scene.objects:
                    context.view_layer.objects.active = obj
                    break
        
        yield
    
    finally:
        # 直接恢复原始状态
        for obj in context.scene.objects:
            obj.select_set(False)
            
        for obj in original_selected:
            if obj and obj.name in context.scene.objects:
                try:
                    obj.select_set(True)
                except ReferenceError:
                    pass
        
        if original_active and original_active.name in context.scene.objects:
            try:
                context.view_layer.objects.active = original_active
            except ReferenceError:
                pass


def create_export_directory(export_path):
    """
    创建导出目录（如果不存在）。
    
    参数:
        export_path (str): 要创建的目录路径。
    
    返回:
        bool: 如果目录存在或已成功创建，则为True。
    """
    if not export_path:
        logger.error("导出路径为空")
        return False
        
    # 处理相对路径（以//开头）
    if export_path.startswith("//"):
        export_path = bpy.path.abspath(export_path)
    
    # 确保路径以分隔符结尾
    if not export_path.endswith(os.path.sep):
        export_path += os.path.sep
    
    # 创建目录（如果不存在）
    if not os.path.exists(export_path):
        try:
            os.makedirs(export_path)
            logger.info(f"创建导出目录: {export_path}")
        except Exception as e:
            logger.error(f"创建导出目录失败: {e}")
            return False
    
    return True


def get_export_path(context, obj_name, settings):
    """
    为给定对象构建完整的导出路径。
    
    参数:
        context (bpy.context): 当前Blender上下文。
        obj_name (str): 要导出的对象名称。
        settings (PropertyGroup): 包含导出设置的属性组。
    
    返回:
        str: 完整的导出路径，包括文件名和扩展名。
    """
    # 获取基本路径
    export_path = settings.mesh_export_path
    
    # 处理相对路径（以//开头）
    if export_path.startswith("//"):
        export_path = bpy.path.abspath(export_path)
    
    # 确保路径以分隔符结尾
    if not export_path.endswith(os.path.sep):
        export_path += os.path.sep
    
    # 构建文件名
    filename = f"{settings.mesh_export_prefix}{obj_name}{settings.mesh_export_suffix}"
    
    # 添加扩展名
    format_ext = settings.mesh_export_format.lower()
    if format_ext == "gltf":
        format_ext = "glb"  # 使用二进制glTF
    
    full_path = f"{export_path}{filename}.{format_ext}"
    return full_path


def get_lod_export_path(context, obj_name, settings, lod_level):
    """
    为给定对象的LOD级别构建完整的导出路径。
    
    参数:
        context (bpy.context): 当前Blender上下文。
        obj_name (str): 要导出的对象名称。
        settings (PropertyGroup): 包含导出设置的属性组。
        lod_level (int): LOD级别（0-4）。
    
    返回:
        str: 完整的LOD导出路径，包括文件名和扩展名。
    """
    # 获取基本路径
    export_path = settings.mesh_export_path
    
    # 处理相对路径（以//开头）
    if export_path.startswith("//"):
        export_path = bpy.path.abspath(export_path)
    
    # 确保路径以分隔符结尾
    if not export_path.endswith(os.path.sep):
        export_path += os.path.sep
    
    # 构建文件名
    filename = f"{settings.mesh_export_prefix}{obj_name}{settings.mesh_export_suffix}_LOD{lod_level}"
    
    # 添加扩展名
    format_ext = settings.mesh_export_format.lower()
    if format_ext == "gltf":
        format_ext = "glb"  # 使用二进制glTF
    
    full_path = f"{export_path}{filename}.{format_ext}"
    return full_path


def create_lod_mesh(context, obj, ratio, lod_type="COLLAPSE", symmetry=False, symmetry_axis="X"):
    """
    为给定对象创建LOD网格。
    
    参数:
        context (bpy.context): 当前Blender上下文。
        obj (bpy.types.Object): 要为其创建LOD的对象。
        ratio (float): 减少比率（0.0-1.0）。
        lod_type (str): 减少类型（COLLAPSE或DECIMATE）。
        symmetry (bool): 是否保持对称性。
        symmetry_axis (str): 对称轴（X、Y或Z）。
    
    返回:
        bpy.types.Object: 新创建的LOD对象，如果失败则为None。
    """
    if obj is None or obj.type != "MESH":
        return None
    
    # 创建对象的副本
    lod_obj = obj.copy()
    lod_obj.data = obj.data.copy()
    context.collection.objects.link(lod_obj)
    
    # 设置活动对象
    with temp_selection_context(context, active_object=lod_obj, selected_objects=[lod_obj]):
        # 应用所有修改器
        for modifier in lod_obj.modifiers:
            try:
                bpy.ops.object.modifier_apply(modifier=modifier.name)
            except Exception as e:
                logger.warning(f"应用修改器'{modifier.name}'失败: {e}")
        
        # 添加减少修改器
        if lod_type == "COLLAPSE":
            modifier = lod_obj.modifiers.new(name="LOD_Collapse", type="DECIMATE")
            modifier.decimate_type = "COLLAPSE"
            modifier.ratio = ratio
            modifier.use_symmetry = symmetry
            modifier.symmetry_axis = symmetry_axis
        else:  # DECIMATE
            modifier = lod_obj.modifiers.new(name="LOD_Decimate", type="DECIMATE")
            modifier.decimate_type = "UNSUBDIV"
            # 转换比率（0-1）为迭代次数（1-6）
            iterations = max(1, min(6, int((1.0 - ratio) * 6)))
            modifier.iterations = iterations
        
        # 应用修改器
        try:
            bpy.ops.object.modifier_apply(modifier=modifier.name)
        except Exception as e:
            logger.error(f"应用LOD修改器失败: {e}")
            bpy.data.objects.remove(lod_obj)
            return None
    
    return lod_obj


def export_object(context, obj, export_path, settings):
    """
    导出单个对象到指定路径。
    
    参数:
        context (bpy.context): 当前Blender上下文。
        obj (bpy.types.Object): 要导出的对象。
        export_path (str): 导出文件的完整路径。
        settings (PropertyGroup): 包含导出设置的属性组。
    
    返回:
        bool: 如果导出成功，则为True。
    """
    if obj is None or obj.type != "MESH":
        return False
    
    # 创建对象的副本
    export_obj = obj.copy()
    export_obj.data = obj.data.copy()
    context.collection.objects.link(export_obj)
    
    # 如果启用了零位置，重置位置
    if settings.mesh_export_zero_location:
        export_obj.location = (0, 0, 0)
    
    # 设置活动对象
    with temp_selection_context(context, active_object=export_obj, selected_objects=[export_obj]):
        # 应用所有修改器
        for modifier in export_obj.modifiers:
            try:
                bpy.ops.object.modifier_apply(modifier=modifier.name)
            except Exception as e:
                logger.warning(f"应用修改器'{modifier.name}'失败: {e}")
        
        # 如果启用了三角化，添加三角化修改器
        if settings.mesh_export_tri:
            modifier = export_obj.modifiers.new(name="Triangulate", type="TRIANGULATE")
            modifier.quad_method = settings.mesh_export_tri_method
            modifier.keep_custom_normals = settings.mesh_export_keep_normals
            
            # 应用三角化修改器
            try:
                bpy.ops.object.modifier_apply(modifier=modifier.name)
            except Exception as e:
                logger.warning(f"应用三角化修改器失败: {e}")
        
        # 根据格式导出
        format = settings.mesh_export_format
        success = False
        
        try:
            if format == "FBX":
                bpy.ops.export_scene.fbx(
                    filepath=export_path,
                    use_selection=True,
                    object_types={'MESH'},
                    use_mesh_modifiers=True,
                    mesh_smooth_type=settings.mesh_export_smoothing,
                    add_leaf_bones=False,
                    bake_anim=False,
                    use_custom_props=False,
                    axis_forward=settings.mesh_export_coord_forward,
                    axis_up=settings.mesh_export_coord_up,
                    global_scale=settings.mesh_export_scale,
                    path_mode='COPY',
                    embed_textures=True,
                    use_tspace=True
                )
                success = True
            
            elif format == "OBJ":
                bpy.ops.export_scene.obj(
                    filepath=export_path,
                    use_selection=True,
                    use_mesh_modifiers=True,
                    axis_forward=settings.mesh_export_coord_forward,
                    axis_up=settings.mesh_export_coord_up,
                    global_scale=settings.mesh_export_scale,
                    path_mode='COPY',
                    use_materials=settings.mesh_export_materials
                )
                success = True
            
            elif format == "GLTF":
                bpy.ops.export_scene.gltf(
                    filepath=export_path,
                    use_selection=True,
                    export_format='GLB',
                    export_materials=settings.mesh_export_materials,
                    export_normals=True,
                    export_tangents=True,
                    export_attributes=True,
                    export_extras=False,
                    export_cameras=False,
                    export_lights=False
                )
                success = True
            
            elif format == "USD":
                bpy.ops.wm.usd_export(
                    filepath=export_path,
                    selected_objects_only=True,
                    export_materials=settings.mesh_export_materials,
                    export_textures=settings.mesh_export_materials,
                    export_normals=True,
                    export_uvmaps=True,
                    export_mesh_colors=True,
                    export_world_space=not settings.mesh_export_zero_location,
                    export_animation=False
                )
                success = True
            
            elif format == "STL":
                bpy.ops.export_mesh.stl(
                    filepath=export_path,
                    use_selection=True,
                    global_scale=settings.mesh_export_scale,
                    use_mesh_modifiers=True,
                    axis_forward=settings.mesh_export_coord_forward,
                    axis_up=settings.mesh_export_coord_up
                )
                success = True
            
            else:
                logger.error(f"不支持的导出格式: {format}")
                success = False
            
        except Exception as e:
            logger.error(f"导出失败: {e}")
            success = False
    
    # 清理临时对象
    bpy.data.objects.remove(export_obj)
    
    return success


# --- 操作符 ---


class MESH_OT_batch_export(Operator):
    """批量导出选定的网格对象"""
    bl_idname = "mesh.batch_export"
    bl_label = "批量导出网格"
    bl_description = "将选定的网格对象导出为指定格式"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        settings = context.scene.mesh_exporter
        selected_objects = [obj for obj in context.selected_objects if obj.type == "MESH"]
        
        if not selected_objects:
            self.report({'ERROR'}, "未选择网格对象")
            return {'CANCELLED'}
        
        # 创建导出目录
        if not create_export_directory(settings.mesh_export_path):
            self.report({'ERROR'}, "无法创建导出目录")
            return {'CANCELLED'}
        
        # 跟踪导出统计
        total_exported = 0
        total_lods = 0
        failed_exports = []
        
        # 导出每个选定的对象
        for obj in selected_objects:
            # 获取导出路径
            export_path = get_export_path(context, obj.name, settings)
            
            # 导出主对象
            if export_object(context, obj, export_path, settings):
                total_exported += 1
                # 标记为已导出
                indicators.mark_object_as_exported(obj)
                logger.info(f"导出成功: {obj.name} -> {export_path}")
            else:
                failed_exports.append(obj.name)
                logger.error(f"导出失败: {obj.name}")
            
            # 如果启用了LOD生成
            if settings.mesh_export_lod and settings.mesh_export_lod_count > 0:
                # 获取LOD比率
                lod_ratios = [
                    settings.mesh_export_lod_ratio_01 if settings.mesh_export_lod_count >= 1 else 0,
                    settings.mesh_export_lod_ratio_02 if settings.mesh_export_lod_count >= 2 else 0,
                    settings.mesh_export_lod_ratio_03 if settings.mesh_export_lod_count >= 3 else 0,
                    settings.mesh_export_lod_ratio_04 if settings.mesh_export_lod_count >= 4 else 0
                ]
                
                # 为每个LOD级别创建和导出网格
                for i in range(settings.mesh_export_lod_count):
                    if lod_ratios[i] <= 0:
                        continue
                    
                    # 创建LOD网格
                    lod_obj = create_lod_mesh(
                        context, obj, lod_ratios[i],
                        lod_type=settings.mesh_export_lod_type,
                        symmetry=settings.mesh_export_lod_symmetry,
                        symmetry_axis=settings.mesh_export_lod_symmetry_axis
                    )
                    
                    if lod_obj:
                        # 获取LOD导出路径
                        lod_export_path = get_lod_export_path(context, obj.name, settings, i+1)
                        
                        # 导出LOD对象
                        if export_object(context, lod_obj, lod_export_path, settings):
                            total_lods += 1
                            logger.info(f"LOD导出成功: {obj.name} (LOD{i+1}) -> {lod_export_path}")
                        else:
                            failed_exports.append(f"{obj.name}_LOD{i+1}")
                            logger.error(f"LOD导出失败: {obj.name} (LOD{i+1})")
                        
                        # 清理LOD对象
                        bpy.data.objects.remove(lod_obj)
        
        # 报告结果
        if total_exported > 0:
            message = f"成功导出 {total_exported} 个对象"
            if total_lods > 0:
                message += f" 和 {total_lods} 个LOD网格"
            self.report({'INFO'}, message)
        
        if failed_exports:
            self.report({'WARNING'}, f"导出失败: {', '.join(failed_exports)}")
        
        if total_exported == 0 and total_lods == 0:
            self.report({'ERROR'}, "没有成功导出任何对象")
            return {'CANCELLED'}
        
        return {'FINISHED'}


class MESH_OT_clear_export_indicators(Operator):
    """清除选定对象的导出指示器"""
    bl_idname = "mesh.clear_export_indicators"
    bl_label = "清除导出指示器"
    bl_description = "清除选定对象的导出状态指示器"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        selected_objects = [obj for obj in context.selected_objects if obj.type == "MESH"]
        
        if not selected_objects:
            self.report({'ERROR'}, "未选择网格对象")
            return {'CANCELLED'}
        
        count = 0
        for obj in selected_objects:
            if indicators.clear_export_indicators(obj):
                count += 1
        
        if count > 0:
            self.report({'INFO'}, f"已清除 {count} 个对象的导出指示器")
        else:
            self.report({'INFO'}, "没有找到要清除的导出指示器")
        
        return {'FINISHED'}


class MESH_OT_clear_all_export_indicators(Operator):
    """清除所有对象的导出指示器"""
    bl_idname = "mesh.clear_all_export_indicators"
    bl_label = "清除所有导出指示器"
    bl_description = "清除场景中所有对象的导出状态指示器"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        mesh_objects = [obj for obj in bpy.data.objects if obj.type == "MESH"]
        
        count = 0
        for obj in mesh_objects:
            if indicators.clear_export_indicators(obj):
                count += 1
        
        if count > 0:
            self.report({'INFO'}, f"已清除 {count} 个对象的导出指示器")
        else:
            self.report({'INFO'}, "没有找到要清除的导出指示器")
        
        return {'FINISHED'}


# 注册的类列表
classes = (
    MESH_OT_batch_export,
    MESH_OT_clear_export_indicators,
    MESH_OT_clear_all_export_indicators,
)