# -*- coding: utf-8 -*-
"""
包含PopTools插件中ReTex模块的属性定义。
定义了纹理重命名和调整大小所需的属性。
"""

import bpy
from bpy.props import BoolProperty, EnumProperty, StringProperty

# 定义分辨率预设选项
resolution_items = [
    ('128', '128 x 128', ''),
    ('256', '256 x 256', ''),
    ('512', '512 x 512', ''),
    ('1024', '1024 x 1024', '')
]

# 初始化属性
def init_properties():
    bpy.types.Scene.rt_replace_prefix = BoolProperty(
        name="替换为'tex'前缀",
        description="将纹理名称的前缀替换为'tex'",
        default=False
    )
    
    # 添加分辨率预设属性
    bpy.types.Scene.rt_resolution_preset = EnumProperty(
        items=resolution_items,
        name="分辨率预设",
        description="纹理调整大小的预设分辨率",
        default='1024'
    )
    
    # 添加ItemLand输入框属性
    bpy.types.Scene.rt_item_land = StringProperty(
        name="ItemLand",
        description="智能对象重命名的前缀",
        default="land"
    )

    # 存储自定义体型，逗号分隔
    bpy.types.Scene.rt_custom_body_types = StringProperty(
        name="自定义体型",
        description="用户添加的自定义体型，以逗号分隔",
        default=""
    )

    # 动态生成体型选项
    def get_body_type_items(self, context):
        default_types = [
            ('man', 'Man', '标准男性'),
            ('woman', 'Woman', '标准女性'),
            ('fatman', 'Fatman', '胖男性'),
            ('fatwoman', 'Fatwoman', '胖女性'),
            ('kid', 'Kid', '小孩')
        ]
        custom_types_str = context.scene.rt_custom_body_types
        custom_types_list = []
        if custom_types_str:
            custom_types_list = [(t.strip(), t.strip().capitalize(), f'自定义: {t.strip()}') for t in custom_types_str.split(',') if t.strip()]
        return default_types + custom_types_list

    bpy.types.Scene.rt_character_body_type = EnumProperty(
        name="体型",
        description="选择角色体型",
        items=get_body_type_items
    )

    bpy.types.Scene.rt_character_serial_number = StringProperty(
        name="序号",
        description="输入角色序号",
        default="001"
    )

# 清除属性
def clear_properties():
    del bpy.types.Scene.rt_replace_prefix
    del bpy.types.Scene.rt_resolution_preset
    del bpy.types.Scene.rt_item_land
    del bpy.types.Scene.rt_character_body_type
    del bpy.types.Scene.rt_character_serial_number
    del bpy.types.Scene.rt_custom_body_types

# 注册函数
def register():
    init_properties()

# 注销函数
def unregister():
    clear_properties()