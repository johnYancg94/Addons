# -*- coding: utf-8 -*-
"""
Vertex to Bone Baker 模块初始化文件
"""

import bpy
from . import operators, panels, properties


def register():
    """注册模块"""
    bpy.utils.register_class(properties.VTBB_Properties)
    bpy.utils.register_class(operators.VTBB_OT_CreateEmptiesForBones)
    bpy.utils.register_class(operators.VTBB_OT_BindEmptiesToVertices)
    bpy.utils.register_class(panels.VTBB_PT_MainPanel)
    
    # 将属性添加到场景中
    bpy.types.Scene.vtbb_props = bpy.props.PointerProperty(type=properties.VTBB_Properties)
    
    print("Vertex to Bone Baker 模块注册完成")


def unregister():
    """注销模块"""
    bpy.utils.unregister_class(panels.VTBB_PT_MainPanel)
    bpy.utils.unregister_class(operators.VTBB_OT_BindEmptiesToVertices)
    bpy.utils.unregister_class(operators.VTBB_OT_CreateEmptiesForBones)
    bpy.utils.unregister_class(properties.VTBB_Properties)
    
    # 从场景中移除属性
    del bpy.types.Scene.vtbb_props
    
    print("Vertex to Bone Baker 模块注销完成")