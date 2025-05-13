# -*- coding: utf-8 -*-
"""
处理导出对象的视觉指示器（对象颜色变化）。

依赖于主导出操作符设置的自定义属性：
- mesh_export_timestamp: 导出时间。
- mesh_export_status: 当前状态（FRESH, STALE, NONE）。

要查看颜色变化，用户需要在实体显示模式下将3D视图着色颜色类型设置为"对象"。
"""

import bpy
import time
import logging
from enum import Enum
from bpy.types import Operator

# --- 设置日志记录器 ---
logger = logging.getLogger(__name__)
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter("%(name)s:%(levelname)s: %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)  # 默认级别

# --- 常量 ---

class ExportStatus(Enum):
    """基于时间表示导出状态的枚举。"""
    FRESH = 0   # 刚刚导出（绿色）
    STALE = 1   # 一段时间前导出（黄色）
    NONE = 2    # 不需要指示器 / 已过期


# 时间常量（秒）
FRESH_DURATION_SECONDS = 60     # 1分钟
STALE_DURATION_SECONDS = 300    # 5分钟


# 自定义属性名称
EXPORT_TIME_PROP = "mesh_export_timestamp"
EXPORT_STATUS_PROP = "mesh_export_status"
ORIGINAL_COLOUR_PROP = "mesh_exporter_original_colour"

# 导出状态颜色（RGBA元组）
STATUS_COLOURS = {
    ExportStatus.FRESH.value: (0.2, 0.8, 0.2, 1.0),  # 绿色
    ExportStatus.STALE.value: (0.8, 0.8, 0.2, 1.0),  # 黄色
}

# 计时器间隔
_TIMER_INTERVAL_SECONDS = 5.0


# --- 核心函数 ---


def mark_object_as_exported(obj):
    """
    将对象标记为刚刚导出，通过设置自定义属性。
    这用于跟踪对象的导出状态。
    
    参数:
        obj (bpy.types.Object): 要标记为已导出的对象。
    
    返回:
        None
    """
    if obj is None or obj.type != "MESH":
        return
        
    # 确保计时器已注册
    if not bpy.app.timers.is_registered(update_timer_callback):
        logger.warning("导出指示器计时器未注册 - "
                       "现在注册")
        try:
            bpy.app.timers.register(
                update_timer_callback,
                first_interval=_TIMER_INTERVAL_SECONDS,
                persistent=True
            )
        except Exception as e:
            logger.error(f"在mark_object_as_exported中注册计时器失败: {e}")
    
    # 标记对象
    obj[EXPORT_TIME_PROP] = time.time()
    obj[EXPORT_STATUS_PROP] = ExportStatus.FRESH.value
    set_object_colour(obj)
    logger.info(f"将{obj.name}标记为刚刚导出")

def _delete_prop(obj, prop_name):
    """
    如果存在，安全地从对象中删除自定义属性。
    
    参数:
        obj (bpy.types.Object): 要修改的对象。
        prop_name (str): 要删除的属性名称。
    
    返回:
        bool: 如果属性被删除则为True，否则为False。
    """
    if obj and prop_name in obj:
        try:
            del obj[prop_name]
            return True
        except (KeyError, AttributeError):
            pass
    return False


def clear_export_indicators(obj):
    """
    清除对象上的所有导出指示器属性和颜色。
    
    参数:
        obj (bpy.types.Object): 要清除的对象。
    
    返回:
        bool: 如果指示器被清除则为True，否则为False。
    """
    if obj is None:
        return False
        
    # 删除所有相关属性
    _delete_prop(obj, EXPORT_TIME_PROP)
    _delete_prop(obj, EXPORT_STATUS_PROP)
    
    # 恢复原始颜色
    restore_object_colour(obj)
    
    return True


def set_object_colour(obj):
    """
    基于对象的导出状态设置其颜色。
    
    参数:
        obj (bpy.types.Object): 要设置颜色的对象。
    
    返回:
        bool: 如果颜色被设置则为True，否则为False。
    """
    if obj is None or EXPORT_STATUS_PROP not in obj:
        return False
        
    status = obj[EXPORT_STATUS_PROP]
    
    # 如果状态无效或为NONE，不做任何事
    if status not in STATUS_COLOURS:
        return False
    
    # 存储原始颜色（如果尚未存储）
    if ORIGINAL_COLOUR_PROP not in obj:
        obj[ORIGINAL_COLOUR_PROP] = obj.color[:]
    
    # 设置新颜色
    obj.color = STATUS_COLOURS[status]
    return True


def restore_object_colour(obj):
    """
    恢复对象的原始颜色（如果已存储）。
    
    参数:
        obj (bpy.types.Object): 要恢复颜色的对象。
    
    返回:
        bool: 如果颜色被恢复则为True，否则为False。
    """
    if obj is None:
        return False
        
    # 如果存储了原始颜色，恢复它
    if ORIGINAL_COLOUR_PROP in obj:
        try:
            obj.color = obj[ORIGINAL_COLOUR_PROP]
            _delete_prop(obj, ORIGINAL_COLOUR_PROP)
            return True
        except (AttributeError, TypeError):
            pass
    
    return False


def update_object_status(obj):
    """
    基于导出时间戳更新对象的导出状态。
    
    参数:
        obj (bpy.types.Object): 要更新的对象。
    
    返回:
        bool: 如果状态被更新则为True，否则为False。
    """
    if obj is None or EXPORT_TIME_PROP not in obj:
        return False
        
    # 获取当前时间和导出时间
    current_time = time.time()
    export_time = obj[EXPORT_TIME_PROP]
    elapsed_time = current_time - export_time
    
    # 确定新状态
    old_status = obj.get(EXPORT_STATUS_PROP, ExportStatus.NONE.value)
    
    if elapsed_time <= FRESH_DURATION_SECONDS:
        new_status = ExportStatus.FRESH.value
    elif elapsed_time <= STALE_DURATION_SECONDS:
        new_status = ExportStatus.STALE.value
    else:
        new_status = ExportStatus.NONE.value
        
    # 如果状态改变，更新它
    if new_status != old_status:
        if new_status == ExportStatus.NONE.value:
            # 如果过期，完全清除指示器
            clear_export_indicators(obj)
        else:
            # 否则更新状态和颜色
            obj[EXPORT_STATUS_PROP] = new_status
            set_object_colour(obj)
        return True
    
    return False


def update_all_objects():
    """
    更新场景中所有对象的导出状态。
    
    返回:
        int: 更新的对象数量。
    """
    count = 0
    
    # 遍历所有对象
    for obj in bpy.data.objects:
        if obj.type == "MESH" and EXPORT_TIME_PROP in obj:
            if update_object_status(obj):
                count += 1
    
    return count


def update_timer_callback():
    """
    更新所有对象的导出状态的计时器回调。
    
    返回:
        float: 下一次调用的间隔（秒）。
    """
    try:
        update_all_objects()
    except Exception as e:
        logger.error(f"更新导出状态时出错: {e}")
    
    # 继续计时器
    return _TIMER_INTERVAL_SECONDS


# --- 操作符 ---


class MESH_OT_clear_export_indicators(Operator):
    """清除所有选定对象的导出指示器"""
    bl_idname = "mesh.clear_export_indicators"
    bl_label = "清除导出指示器"
    bl_description = "从所有选定对象中移除导出状态指示器"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.selected_objects

    def execute(self, context):
        count = 0
        
        # 清除所有选定对象的指示器
        for obj in context.selected_objects:
            if obj.type == "MESH" and clear_export_indicators(obj):
                count += 1
        
        if count > 0:
            self.report({'INFO'}, f"已清除{count}个对象的导出指示器")
        else:
            self.report({'INFO'}, "没有找到要清除的导出指示器")
        
        return {'FINISHED'}


class MESH_OT_clear_all_export_indicators(Operator):
    """清除场景中所有对象的导出指示器"""
    bl_idname = "mesh.clear_all_export_indicators"
    bl_label = "清除所有导出指示器"
    bl_description = "从场景中的所有对象移除导出状态指示器"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        count = 0
        
        # 清除所有对象的指示器
        for obj in bpy.data.objects:
            if obj.type == "MESH" and clear_export_indicators(obj):
                count += 1
        
        if count > 0:
            self.report({'INFO'}, f"已清除{count}个对象的导出指示器")
        else:
            self.report({'INFO'}, "没有找到要清除的导出指示器")
        
        return {'FINISHED'}


# --- 注册/注销 ---


classes = (
    MESH_OT_clear_export_indicators,
    MESH_OT_clear_all_export_indicators,
)


def register():
    """注册导出指示器组件"""
    for cls in classes:
        bpy.utils.register_class(cls)
    
    # 注册计时器（如果尚未注册）
    if not bpy.app.timers.is_registered(update_timer_callback):
        try:
            bpy.app.timers.register(
                update_timer_callback,
                first_interval=_TIMER_INTERVAL_SECONDS,
                persistent=True
            )
            logger.info("已注册导出指示器计时器")
        except Exception as e:
            logger.error(f"注册导出指示器计时器失败: {e}")


def unregister():
    """注销导出指示器组件"""
    # 注销计时器（如果已注册）
    if bpy.app.timers.is_registered(update_timer_callback):
        try:
            bpy.app.timers.unregister(update_timer_callback)
            logger.info("已注销导出指示器计时器")
        except Exception as e:
            logger.error(f"注销导出指示器计时器失败: {e}")
    
    # 注销类
    for cls in reversed(classes):
        try:
            bpy.utils.unregister_class(cls)
        except RuntimeError as e:
            logger.error(f"注销{cls.__name__}失败: {e}")