# -*- coding: utf-8 -*-
"""
包含PopTools插件中ReTex模块的面板定义。
提供纹理管理和重命名功能的用户界面。
"""

import bpy
from bpy.types import Panel

# 定义ReTex面板类
class RT_PT_TextureRenamerPanel(Panel):
    bl_label = "纹理管理"
    bl_idname = "RT_PT_TextureRenamerPanel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'PopTools'
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        
        # 添加智能重命名部分
        box = layout.box()
        box.label(text="智能重命名：")
        row = box.row()
        row.prop(context.scene, "rt_item_land", text="海岛名")
        
        # 添加类型标识符说明
        note_box = box.box()
        note_box.label(text="类型标识符说明：")
        note_box.label(text="b：气球 h：手持 p：堂食 c：头戴")
        
        row = box.row()
        row.operator("rt.smart_rename_objects", text="重命名选中物体", icon='OUTLINER_OB_MESH')
        
        # 添加分隔线
        layout.separator()
        
        # 获取当前勾选框的状态
        replace_prefix = context.scene.rt_replace_prefix
        
        # 创建行布局
        row = layout.row()
        
        # 动态设置图标
        if replace_prefix:
            icon = 'CHECKBOX_HLT'
        else:
            icon = 'CHECKBOX_DEHLT'
        
        # 添加勾选框
        row.prop(context.scene, "rt_replace_prefix", text="替换为'tex'前缀", icon=icon)

        # 添加操作按钮
        row = layout.row()
        row.operator("rt.set_texname_of_object", text="设置对象的纹理名称", icon='OBJECT_DATA')
        row = layout.row()
        row.operator("rt.replace_textures", text="替换所有纹理", icon='FILE_REFRESH')
        
        # 添加分隔线
        layout.separator()
        
        # 添加分辨率设置
        box = layout.box()
        box.label(text="纹理分辨率：")
        row = box.row()
        row.prop(context.scene, "rt_resolution_preset", text="大小")
        row = layout.row()
        row.operator("rt.resize_textures", text="调整纹理大小", icon='IMAGE_DATA')

        # 添加角色重命名部分
        layout.separator()
        char_box = layout.box()
        char_box.label(text="角色重命名：")
        
        row = char_box.row(align=True)
        row.prop(context.scene, "rt_character_body_type", text="体型")
        row.prop(context.scene, "rt_character_serial_number", text="序号")
        
        row = char_box.row(align=True)
        row.operator("rt.rename_character_body", text="命名选中体型")
        row.operator("rt.rename_character_hair", text="命名选中发型")

        # 添加体型管理部分
        add_type_box = char_box.box()
        add_type_box.label(text="添加新体型：")
        row = add_type_box.row(align=True)
        row.prop(context.scene, "rt_new_body_type_input", text="")
        row.operator("rt.add_body_type", text="添加体型")

# 注册的类列表
classes = (
    RT_PT_TextureRenamerPanel,
)

# 注册函数
def register():
    for cls in classes:
        bpy.utils.register_class(cls)

# 注销函数
def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)