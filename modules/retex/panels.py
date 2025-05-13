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
    bl_order = 0 # 设置为第一排
    # bl_options = {'DEFAULT_CLOSED'} # 设置为默认展开

    def draw(self, context):
        layout = self.layout
        
        # 添加智能重命名部分
        box = layout.box()
        box.label(text="海岛配方道具智能重命名：")
        row = box.row()
        row.prop(context.scene, "rt_item_land", text="海岛名")
        
        # 添加类型标识符说明
        note_box = box.box()
        note_box.label(text="类型标识符说明：")
        note_box.label(text="b：气球 h：手持 p：堂食 c：头戴")
       
        
        row = box.row(align=True) # 设置对齐，让按钮更紧凑
        row.operator("rt.show_smart_rename_help", text="", icon='QUESTION') # 添加问号帮助按钮
        row.operator("rt.smart_rename_objects", text="智能重命名选中物体", icon='OUTLINER_OB_MESH')
        
        # 添加分隔线
        layout.separator()

        # 添加打包贴图部分
        pack_box = layout.box()
        row = pack_box.row()
        row.operator("file.pack_all", text="打包贴图", icon='PACKAGE')
        
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
        row.operator("rt.replace_textures", text="同步所有纹理", icon='FILE_REFRESH')
        
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
        
        # 体型控件放在单独的行
        row = char_box.row(align=True)
        row.prop(context.scene, "rt_character_body_type", text="体型")
        
        # 序号控件放在新的行，增加间距
        row = char_box.row(align=True)
        # 使用split创建一个更紧凑的布局
        split = row.split(factor=0.3)
        split.label(text="序号:")
        split.prop(context.scene, "rt_character_serial_number", text="")
        op_decrease = row.operator("rt.adjust_serial_number", text="", icon='TRIA_LEFT')
        op_decrease.target_property = "rt_character_serial_number"
        op_decrease.delta = -1
        op_decrease.min_value = 1
        op_increase = row.operator("rt.adjust_serial_number", text="", icon='TRIA_RIGHT')
        op_increase.target_property = "rt_character_serial_number"
        op_increase.delta = 1
        op_increase.min_value = 1
        
        row = char_box.row(align=True)
        row.operator("rt.rename_character_body", text="命名选中体型")
        row.operator("rt.rename_character_hair", text="命名选中发型")
        
        # 添加同步纹理命名按钮
        row = char_box.row(align=True)
        row.operator("rt.sync_texture_names", text="同步选择模型纹理命名", icon='FILE_REFRESH')

        # 添加动物重命名部分
        layout.separator()
        animal_box = layout.box()
        animal_box.label(text="动物重命名：")
        
        # 体型控件放在单独的行
        row = animal_box.row(align=True)
        row.prop(context.scene, "rt_animal_body_type", text="体型")
        
        # 序号控件放在新的行，增加间距
        row = animal_box.row(align=True)
        # 使用split创建一个更紧凑的布局
        split = row.split(factor=0.3)
        split.label(text="序号:")
        split.prop(context.scene, "rt_animal_serial_number", text="")
        op_decrease = row.operator("rt.adjust_serial_number", text="", icon='TRIA_LEFT')
        op_decrease.target_property = "rt_animal_serial_number"
        op_decrease.delta = -1
        op_decrease.min_value = 1
        op_increase = row.operator("rt.adjust_serial_number", text="", icon='TRIA_RIGHT')
        op_increase.target_property = "rt_animal_serial_number"
        op_increase.delta = 1
        op_increase.min_value = 1
        
        row = animal_box.row(align=True)
        row.operator("rt.rename_animal", text="命名选中动物")

# 定义3DCoat整理面板类
class RT_PT_3DCoatPanel(Panel):
    bl_label = "导出3DCoat整理"
    bl_idname = "RT_PT_3DCoatPanel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'PopTools'
    bl_order = 1 # 设置为第二排

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        # 添加材质整理部分
        mat_box = layout.box()
        mat_box.label(text="材质整理：")
        row = mat_box.row()
        row.operator("rt.organize_selected_materials", text="一键整理选中模型材质", icon='MATERIAL')

        # 添加UV检查部分
        uv_box = layout.box()
        uv_box.label(text="UV检查：")
        row = uv_box.row()
        row.operator("rt.check_uvs", text="一键检查UV", icon='UV_DATA') # 使用 UV_DATA 作为检查器纹理的近似图标

        # 显示UV检查结果
        if hasattr(scene, 'rt_uv_check_results') and scene.rt_uv_check_results:
            results_box = uv_box.box() # 为UV检查结果创建一个新的框
            if scene.rt_uv_check_results == "所有模型UV正常，无重复UV Map":
                row = results_box.row()
                row.label(text="无重复UV模型", icon='CHECKMARK')
            else:
                results_box.label(text="存在多个UV Map的模型：")
                # 创建一个水平布局来显示模型名称
                flow = results_box.column_flow(columns=4, align=True)
                # 将结果字符串拆分为列表
                items = scene.rt_uv_check_results.split('\n')
                for item in items:
                    if item.strip():
                        # 每个模型名称占据单独一行
                        flow.label(text=item)
        elif hasattr(scene, 'rt_uv_check_triggered') and scene.rt_uv_check_triggered:
            results_box = uv_box.box() # 为UV检查结果创建一个新的框
            # 如果检查已触发但结果为空（可能在操作符中被清空表示无问题）
            row = results_box.row()
            row.label(text="无重复UV模型", icon='CHECKMARK')


# 注册的类列表
classes = (
    RT_PT_TextureRenamerPanel,
    RT_PT_3DCoatPanel, # 添加新的面板类
)

# 注册函数
def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.rt_uv_check_results = bpy.props.StringProperty(name="UV Check Results", default="")
    bpy.types.Scene.rt_uv_check_triggered = bpy.props.BoolProperty(name="UV Check Triggered", default=False)


# 注销函数
def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    # 清理自定义属性
    if hasattr(bpy.types.Scene, 'rt_uv_check_results'):
        del bpy.types.Scene.rt_uv_check_results
    if hasattr(bpy.types.Scene, 'rt_uv_check_triggered'):
        del bpy.types.Scene.rt_uv_check_triggered