# -*- coding: utf-8 -*-
"""
PopTools插件的ReTex模块
提供纹理管理和重命名功能
"""

import bpy
import logging
from . import operators
from . import panels
from . import properties

# 设置日志记录器
logger = logging.getLogger(__name__)
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter("%(name)s:%(levelname)s: %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)  # 默认级别

# 注册的类列表
classes = (
    *operators.classes,
    *panels.classes,
)

# 注册函数
def register():
    logger.info("开始注册 ReTex 模块")
    
    # 1. 首先注册属性
    properties.register()
    logger.info("ReTex 属性已注册")
    
    # 2. 注册其他类（操作符、面板）
    for cls in classes:
        try:
            bpy.utils.register_class(cls)
        except ValueError as e:
            # 类可能已经被注册，记录错误但继续执行
            logger.warning(f"注册类 {cls.__name__} 时出错: {e}")
    logger.info("ReTex 面板/操作符类已注册")
    
    logger.info("ReTex 模块注册完成")

# 注销函数
def unregister():
    logger.info("开始注销 ReTex 模块")
    # 按照与注册相反的顺序注销
    
    # 1. 注销类（操作符、面板）
    for cls in reversed(classes):
        try:
            bpy.utils.unregister_class(cls)
        except RuntimeError as e:
            # 类可能已经被注销，记录错误但继续执行
            logger.warning(f"注销类 {cls.__name__} 时出错: {e}")
    logger.info("ReTex 面板/操作符类已注销")
    
    # 2. 最后注销属性
    properties.unregister()
    logger.info("ReTex 属性已注销")
    
    logger.info("ReTex 模块注销完成")