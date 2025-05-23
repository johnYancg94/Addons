# -*- coding: utf-8 -*-
"""
PopTools插件的ReTex模块
提供纹理管理和重命名功能
"""

import bpy
from . import operators
from . import panels
from . import properties

# 注册函数
def register():
    properties.register()
    operators.register()
    panels.register()

# 注销函数
def unregister():
    panels.unregister()
    operators.unregister()
    properties.unregister()