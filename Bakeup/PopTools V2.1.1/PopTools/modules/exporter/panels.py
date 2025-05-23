# -*- coding: utf-8 -*-
"""
PopTools 网格导出器 UI 面板
本模块包含PopTools插件中网格导出器的UI面板。
它包括主导出面板、LOD设置和最近导出记录。
"""

import time
import logging
from bpy.types import Panel
from . import indicators

# --- 设置日志记录器 ---
logger = logging.getLogger(__name__)
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter("%(name)s:%(levelname)s: %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)  # 默认级别

# 主UI面板
class MESH_PT_exporter_panel(Panel):
    bl_label = "网格批量导出器"
    bl_idname = "MESH_PT_exporter_panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "PopTools" # 修改为PopTools选项卡
    bl_order = 1 # 设置为第二排
    bl_options = {'DEFAULT_CLOSED'} # 设置为默认收起

    # 辅助函数
    def format_has_scale(self, format):
        """检查格式是否兼容缩放导出设置"""
        return format in {"FBX", "OBJ", "STL"}

    def format_has_coordinates(self, format):
        """检查格式是否兼容坐标导出设置"""
        return format in {"FBX", "OBJ", "USD", "STL"}
    
    def format_has_smoothing(self, format):
        """检查格式是否兼容平滑导出设置"""
        return format in {"FBX"}


    def draw(self, context):
        layout = self.layout

        # --- 调试开始 ---
        if not hasattr(context.scene, "mesh_exporter"):
            logger.error("context.scene没有'mesh_exporter'属性！")
            layout.label(text="错误：属性组未注册？")
            return # 如果组不存在，停止绘制
        
        settings = context.scene.mesh_exporter

        if settings is None:
            logger.error("context.scene.mesh_exporter为None！")
            layout.label(text="错误：属性组为None？")
            return # 如果组为None，停止绘制
        # --- 调试结束 ---

        layout.use_property_split = True
        layout.use_property_decorate = False

        # 导出路径设置
        layout.prop(settings, "mesh_export_path")
        layout.prop(settings, "mesh_export_format")

        # 坐标系统设置
        if self.format_has_coordinates(settings.mesh_export_format):
            col = layout.column(heading="坐标系统", align=True)
            row = col.row(align=True)
            row.prop(settings, "mesh_export_coord_up", expand=True)
            row = col.row(align=True)
            row.prop(settings, "mesh_export_coord_forward", expand=True)

        # 缩放设置
        col = layout.column(heading="缩放", align=True)
        col.prop(settings, "mesh_export_scale")

        # 单位设置
        col = layout.column(heading="单位", align=True)
        row = col.row(align=True)
        row.prop(settings, "mesh_export_units", expand=True)

        # 平滑设置
        if self.format_has_smoothing(settings.mesh_export_format):
            # 仅当格式支持平滑时显示
            col = layout.column(heading="平滑", align=True)
            row = col.row(align=True)
            row.prop(settings, "mesh_export_smoothing", expand=True)

        # 零位置设置
        layout.prop(settings, "mesh_export_zero_location")

        # 三角化设置
        layout.prop(settings, "mesh_export_tri")
        if settings.mesh_export_tri:
            col = layout.column()
            col.prop(settings, "mesh_export_tri_method")
            col.prop(settings, "mesh_export_keep_normals")

        # 材质设置
        layout.prop(settings, "mesh_export_materials")

        # 前缀/后缀设置
        col = layout.column(heading="命名", align=True)
        col.prop(settings, "mesh_export_prefix")
        col.prop(settings, "mesh_export_suffix")

        # 导出按钮
        layout.separator()
        row = layout.row(align=True)
        row.scale_y = 1.5
        row.operator("mesh.batch_export", text="导出选定网格", icon="EXPORT")


# LOD设置面板
class MESH_PT_exporter_lod_panel(Panel):
    bl_label = "LOD设置"
    bl_idname = "MESH_PT_exporter_lod_panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "PopTools" # 修改为PopTools选项卡
    bl_parent_id = "MESH_PT_exporter_panel"
    bl_options = {'DEFAULT_CLOSED'}

    def draw_header(self, context):
        settings = context.scene.mesh_exporter
        self.layout.prop(settings, "mesh_export_lod", text="")

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        settings = context.scene.mesh_exporter

        # 如果启用了LOD生成，显示设置
        if settings.mesh_export_lod:
            layout.prop(settings, "mesh_export_lod_count")
            layout.prop(settings, "mesh_export_lod_type")

            # 对称设置
            layout.prop(settings, "mesh_export_lod_symmetry")
            if settings.mesh_export_lod_symmetry:
                layout.prop(settings, "mesh_export_lod_symmetry_axis")

            # LOD比率设置
            layout.separator()
            layout.label(text="LOD比率:")
            col = layout.column(align=True)

            # 根据LOD数量显示比率设置
            if settings.mesh_export_lod_count >= 1:
                col.prop(settings, "mesh_export_lod_ratio_01")
            if settings.mesh_export_lod_count >= 2:
                col.prop(settings, "mesh_export_lod_ratio_02")
            if settings.mesh_export_lod_count >= 3:
                col.prop(settings, "mesh_export_lod_ratio_03")
            if settings.mesh_export_lod_count >= 4:
                col.prop(settings, "mesh_export_lod_ratio_04")


# 最近导出面板
class MESH_PT_exporter_recent_panel(Panel):
    bl_label = "最近导出"
    bl_idname = "MESH_PT_exporter_recent_panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "PopTools" # 修改为PopTools选项卡
    bl_parent_id = "MESH_PT_exporter_panel"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout

        # 显示清除指示器按钮
        row = layout.row()
        row.operator("mesh.clear_export_indicators", text="清除选定", icon="X")
        row.operator("mesh.clear_all_export_indicators", text="清除所有", icon="X")

        # 显示导出状态说明
        box = layout.box()
        col = box.column()
        col.label(text="导出状态颜色:")
        row = col.row()
        row.label(text="绿色 = 最近导出 (<1分钟)")
        row = col.row()
        row.label(text="黄色 = 较早导出 (<5分钟)")


# 注册的类列表
classes = (
    MESH_PT_exporter_panel,
    MESH_PT_exporter_lod_panel,
    MESH_PT_exporter_recent_panel,
)