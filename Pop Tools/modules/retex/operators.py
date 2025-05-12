# -*- coding: utf-8 -*-
"""
包含PopTools插件中ReTex模块的操作符。
提供纹理重命名和调整大小的功能。
"""

import bpy
import os
import re
from bpy.types import Operator

# 定义操作符类：智能重命名物体
class RT_OT_SmartRenameObjects(Operator):
    bl_idname = "rt.smart_rename_objects"
    bl_label = "智能重命名选中物体"
    bl_description = "使用智能命名模式重命名选定的对象"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        selected_objects = bpy.context.selected_objects
        total_renamed = 0
        errors = []
        
        # 获取用户输入的ItemLand值
        item_land = context.scene.rt_item_land
        
        # 定义类型映射字典
        type_mapping = {
            'b': 'balloon',
            'h': 'hand',
            'p': 'part',
            'c': 'cap'
        }
        
        for obj in selected_objects:
            try:
                # 从对象名称中提取数字
                numbers = re.findall(r'\d+', obj.name)
                
                # 从对象名称中提取类型标识符
                type_code = None
                for code in type_mapping.keys():
                    if code in obj.name.lower():
                        type_code = code
                        break
                
                # 如果找到数字和类型标识符
                if numbers and type_code:
                    # 取第一个匹配的数字
                    num = int(numbers[0])
                    # 转换为两位数格式
                    formatted_num = f"{num:02d}"
                    # 获取类型的完整名称
                    type_name = type_mapping[type_code]
                    # 构建新名称：mesh_item_[ItemLand]_[类型]_[数字]
                    new_name = f"mesh_item_{item_land}_{type_name}_{formatted_num}"
                    # 重命名对象
                    obj.name = new_name
                    # 同步设置物体的data name
                    if obj.data:
                        obj.data.name = new_name
                    total_renamed += 1
                else:
                    if not numbers:
                        errors.append(f"重命名失败：{obj.name}\n错误信息：未找到数字")
                    if not type_code:
                        errors.append(f"重命名失败：{obj.name}\n错误信息：未找到有效的类型标识符(b/h/p/c)")
            except Exception as e:
                errors.append(f"重命名失败：{obj.name}\n错误信息：{str(e)}")
        
        # 操作完成后显示结果
        if total_renamed > 0:
            self.report({'INFO'}, f"成功重命名 {total_renamed} 个物体！")
        if errors:
            error_msg = "\n".join(errors)
            self.report({'ERROR'}, f"错误信息：\n{error_msg}")
            
        return {'FINISHED'}

# 定义操作符类：设置对象的纹理名称
class RT_OT_SetTexnameOfObject(Operator):
    bl_idname = "rt.set_texname_of_object"
    bl_label = "设置对象的纹理名称"
    bl_description = "根据选定对象的名称重命名纹理"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        selected_objects = bpy.context.selected_objects
        total_renamed = 0
        errors = []
        
        for obj in selected_objects:
            if obj.material_slots:
                material_slot = obj.material_slots[0]
                material = material_slot.material
                if material and material.node_tree:
                    for node in material.node_tree.nodes:
                        if node.type == 'TEX_IMAGE':
                            image = node.image
                            if image:
                                try:
                                    # 获取图片文件路径
                                    filepath = bpy.path.abspath(image.filepath)
                                    if not filepath:
                                        continue
                                        
                                    # 获取目录和扩展名
                                    directory = os.path.dirname(filepath)
                                    extension = os.path.splitext(filepath)[1]
                                    
                                    # 构建新的文件名
                                    new_name = obj.name
                                    if context.scene.rt_replace_prefix:
                                        # 检查是否已有前缀，如果有则替换为tex_，否则添加tex_前缀
                                        prefix_match = re.match(r'^([a-zA-Z]+)_(.+)$', new_name)
                                        if prefix_match:
                                            # 替换现有前缀
                                            new_name = "tex_" + prefix_match.group(2)
                                        else:
                                            # 添加前缀
                                            new_name = "tex_" + new_name
                                        
                                    new_filepath = os.path.join(directory, new_name + extension)
                                    
                                    # 如果新文件名已存在，添加数字后缀
                                    counter = 1
                                    while os.path.exists(new_filepath) and new_filepath != filepath:
                                        base_name = obj.name
                                        new_name = f"{base_name}_{counter}"
                                        if context.scene.rt_replace_prefix:
                                            # 检查是否已有前缀，如果有则替换为tex_，否则添加tex_前缀
                                            prefix_match = re.match(r'^([a-zA-Z]+)_(.+)$', new_name)
                                            if prefix_match:
                                                # 替换现有前缀
                                                new_name = "tex_" + prefix_match.group(2)
                                            else:
                                                # 添加前缀
                                                new_name = "tex_" + new_name
                                        new_filepath = os.path.join(directory, new_name + extension)
                                        counter += 1
                                    
                                    # 重命名文件
                                    if filepath != new_filepath:
                                        os.rename(filepath, new_filepath)
                                        image.filepath = new_filepath
                                        image.name = new_name
                                        total_renamed += 1
                                        
                                except Exception as e:
                                    errors.append(f"重命名失败：{image.name}\n错误信息：{str(e)}")
        
        # 操作完成后显示结果
        if total_renamed > 0:
            self.report({'INFO'}, f"成功重命名 {total_renamed} 个纹理！")
        if errors:
            error_msg = "\n".join(errors)
            self.report({'ERROR'}, f"错误信息：\n{error_msg}")
            
        return {'FINISHED'}

# 定义操作符类：替换所有纹理
class RT_OT_ReplaceTextures(Operator):
    bl_idname = "rt.replace_textures"
    bl_label = "替换所有纹理"
    bl_description = "将所有纹理名称替换为与其内部名称匹配"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        total_renamed = 0
        errors = []
        
        # 遍历所有图片
        for image in bpy.data.images:
            if image.filepath:
                try:
                    # 获取图片文件路径
                    filepath = bpy.path.abspath(image.filepath)
                    if not filepath or not os.path.exists(filepath):
                        continue
                        
                    # 获取目录和扩展名
                    directory = os.path.dirname(filepath)
                    extension = os.path.splitext(filepath)[1]
                    
                    # 构建新的文件名
                    new_name = image.name
                    if context.scene.rt_replace_prefix:
                        # 检查是否已有前缀，如果有则替换为tex_，否则添加tex_前缀
                        prefix_match = re.match(r'^([a-zA-Z]+)_(.+)$', new_name)
                        if prefix_match:
                            # 替换现有前缀
                            new_name = "tex_" + prefix_match.group(2)
                        elif not new_name.startswith("tex_"):
                            # 添加前缀
                            new_name = "tex_" + new_name
                            
                    new_filepath = os.path.join(directory, new_name + extension)
                    
                    # 如果新文件名已存在，添加数字后缀
                    counter = 1
                    while os.path.exists(new_filepath) and new_filepath != filepath:
                        base_name = new_name.rsplit('_', 1)[0] if '_' in new_name else new_name
                        new_name = f"{base_name}_{counter}"
                        new_filepath = os.path.join(directory, new_name + extension)
                        counter += 1
                    
                    # 重命名文件
                    if filepath != new_filepath:
                        os.rename(filepath, new_filepath)
                        image.filepath = new_filepath
                        total_renamed += 1
                        
                except Exception as e:
                    errors.append(f"重命名失败：{image.name}\n错误信息：{str(e)}")
        
        # 操作完成后显示结果
        if total_renamed > 0:
            self.report({'INFO'}, f"成功重命名 {total_renamed} 个纹理！")
        if errors:
            error_msg = "\n".join(errors)
            self.report({'ERROR'}, f"错误信息：\n{error_msg}")
            
        return {'FINISHED'}

# 定义操作符类：调整纹理大小
class RT_OT_ResizeTextures(Operator):
    bl_idname = "rt.resize_textures"
    bl_label = "调整纹理大小"
    bl_description = "将选定的纹理调整为指定的分辨率并自动保存到Small文件夹"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        selected_objects = bpy.context.selected_objects
        total_resized = 0
        total_skipped = 0
        total_saved = 0
        errors = []
        
        # 获取目标分辨率
        resolution = context.scene.rt_resolution_preset
        target_size = int(resolution)

        # 处理的图像列表，用于避免重复处理同一图像
        processed_images = set()

        # 收集所有需要处理的图像
        images_to_process = []
        for obj in selected_objects:
            if obj.material_slots:
                material_slot = obj.material_slots[0]
                material = material_slot.material
                if material and material.node_tree:
                    for node in material.node_tree.nodes:
                        if node.type == 'TEX_IMAGE':
                            image = node.image
                            if image and image.name not in processed_images:
                                # 记录已处理的图像
                                processed_images.add(image.name)
                                # 添加到待处理列表
                                images_to_process.append(image)
        
        # 如果没有找到任何图像，提前返回
        if not images_to_process:
            self.report({'WARNING'}, "未找到任何可处理的纹理！请确保选中的对象包含有效的纹理。")
            return {'CANCELLED'}
        
        # 处理每个图像
        for image in images_to_process:
            try:
                # 检查图像是否有数据
                if not image.has_data:
                    # 尝试重新加载图像
                    try:
                        # 先卸载图像再重新加载
                        image.reload()
                    except:
                        pass
                    
                    # 再次检查图像是否有数据
                    if not image.has_data:
                        total_skipped += 1
                        continue
                
                # 调整图像分辨率
                image.scale(target_size, target_size)
                total_resized += 1
                
                # 自动保存到Small文件夹
                try:
                    # 获取原始图像路径
                    original_path = bpy.path.abspath(image.filepath)
                    if original_path:
                        # 获取文件名和扩展名
                        filename = os.path.basename(original_path)
                        directory = os.path.dirname(original_path)
                        
                        # 获取根目录
                        root_dir = directory

                        # 创建Small文件夹（如果不存在）
                        small_dir = os.path.join(root_dir, "Small")
                        if not os.path.exists(small_dir):
                            os.makedirs(small_dir)
                        
                        # 创建Small文件夹（如果不存在）
                        small_dir = os.path.join(root_dir, "Small")
                        if not os.path.exists(small_dir):
                            os.makedirs(small_dir)
                        
                        # 构建新的保存路径
                        save_path = os.path.join(small_dir, filename)
                        
                        # 保存图像
                        image.save_render(save_path)
                        total_saved += 1
                except Exception as e:
                    errors.append(f"保存失败：{image.name}\n错误信息：{str(e)}")
                
            except Exception as e:
                # 提供更详细的错误信息
                error_msg = str(e)
                if "does not have any image data" in error_msg:
                    errors.append(f"处理失败：{image.name}\n错误信息：图像没有数据，请确保图像已正确加载。尝试在Blender中打开图像编辑器并手动加载该图像。")
                else:
                    errors.append(f"处理失败：{image.name}\n错误信息：{error_msg}")

        # 操作完成后显示结果
        if total_resized > 0:
            success_msg = f"成功调整 {total_resized} 个纹理的分辨率！"
            if total_saved > 0:
                success_msg += f"并保存 {total_saved} 个纹理到Small文件夹。"
            if total_skipped > 0:
                success_msg += f"跳过 {total_skipped} 个没有图像数据的纹理。"
            self.report({'INFO'}, success_msg)
        elif total_skipped > 0:
            self.report({'WARNING'}, f"没有纹理被调整，跳过了 {total_skipped} 个没有图像数据的纹理。")
        else:
            self.report({'WARNING'}, "未找到任何可处理的纹理！")
            
        if errors:
            error_msg = "\n".join(errors)
            self.report({'ERROR'}, f"错误信息：\n{error_msg}")

        return {'FINISHED'}

# 定义操作符类：命名选中体型
class RT_OT_RenameCharacterBody(Operator):
    bl_idname = "rt.rename_character_body"
    bl_label = "命名选中体型"
    bl_description = "根据选择的体型和序号重命名选中的角色模型"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scene = context.scene
        selected_objects = bpy.context.selected_objects
        body_type = scene.rt_character_body_type
        serial_number = scene.rt_character_serial_number

        if not selected_objects:
            self.report({'WARNING'}, "没有选中的模型")
            return {'CANCELLED'}

        if not serial_number.isdigit():
            self.report({'ERROR'}, "序号必须是数字")
            return {'CANCELLED'}

        renamed_count = 0
        for obj in selected_objects:
            if obj.type == 'MESH':
                new_name = f"mesh_characters_{body_type}_{serial_number}"
                obj.name = new_name
                if obj.data:
                    obj.data.name = new_name
                renamed_count += 1
        
        if renamed_count > 0:
            self.report({'INFO'}, f"成功重命名 {renamed_count} 个体型模型")
        else:
            self.report({'INFO'}, "没有符合条件的模型被重命名")
        return {'FINISHED'}

# 定义操作符类：命名选中发型
class RT_OT_RenameCharacterHair(Operator):
    bl_idname = "rt.rename_character_hair"
    bl_label = "命名选中发型"
    bl_description = "根据选择的体型和序号重命名选中的发型模型"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scene = context.scene
        selected_objects = bpy.context.selected_objects
        body_type = scene.rt_character_body_type
        serial_number = scene.rt_character_serial_number

        if not selected_objects:
            self.report({'WARNING'}, "没有选中的模型")
            return {'CANCELLED'}

        if not serial_number.isdigit():
            self.report({'ERROR'}, "序号必须是数字")
            return {'CANCELLED'}

        renamed_count = 0
        for obj in selected_objects:
            if obj.type == 'MESH':
                new_name = f"mesh_head_{body_type}_head{serial_number}" # 注意这里的命名格式是 mesh_head_{体型}_head{序号}
                obj.name = new_name
                if obj.data:
                    obj.data.name = new_name
                renamed_count += 1
        
        if renamed_count > 0:
            self.report({'INFO'}, f"成功重命名 {renamed_count} 个发型模型")
        else:
            self.report({'INFO'}, "没有符合条件的模型被重命名")
        return {'FINISHED'}

# 注册所有操作符
classes = (
    RT_OT_SmartRenameObjects,
    RT_OT_SetTexnameOfObject,
    RT_OT_ReplaceTextures,
    RT_OT_ResizeTextures,
    RT_OT_RenameCharacterBody,
    RT_OT_RenameCharacterHair
)

# 注册函数
def register():
    for cls in classes:
        bpy.utils.register_class(cls)

# 注销函数
def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)