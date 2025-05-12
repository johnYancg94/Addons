# -*- coding: utf-8 -*-
"""
This module defines properties for exporting meshes in Blender.
It includes properties for export path, format, scale, coordinate system,
triangulation, LOD generation, and more.
"""

import bpy
from bpy.props import (StringProperty, EnumProperty, 
                      FloatProperty, IntProperty, BoolProperty,
                      PointerProperty)
from bpy.types import PropertyGroup
import logging

# --- Setup Logger ---
logger = logging.getLogger(__name__)
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter("%(name)s:%(levelname)s: %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)  # Default level


class MeshExporterSettings(PropertyGroup):
    # Export path property
    # Default to the current blend file directory 
    # with a subfolder "exported_meshes"
    mesh_export_path: StringProperty(
        name="导出路径",
        description="导出网格的路径",
        default="//exported_meshes/",
        subtype="DIR_PATH"
    )

    # Export format property
    mesh_export_format: EnumProperty(
        name="格式",
        description="导出网格的文件格式",
        items=[
             ("FBX", "FBX", "导出为FBX"),
             ("OBJ", "OBJ", "导出为OBJ"),
             ("GLTF", "glTF", "导出为glTF"),
             ("USD", "USD", "导出为USD"),
             ("STL", "STL", "导出为STL"),
        ],
        default="FBX"
    )

    # Scale property
    mesh_export_scale: FloatProperty(
        name="缩放",
        description="导出网格的缩放因子",
        default=1.0,
        min=0.001,
        max=1000.0,
        soft_min=0.01,
        soft_max=100.0
    )
    
    # Units property
    mesh_export_units: EnumProperty(
        name="单位",
        description="导出网格的单位系统",
        items=[
            ("METERS", "米", "使用米作为单位"),
            ("CENTIMETERS", "厘米", "使用厘米作为单位"),
        ],
        default="METERS",
    )

    # Coordinate system properties
    mesh_export_coord_up: EnumProperty(
        name="向上轴",
        description="导出网格的向上轴",
        items=[
            ("X", "X", ""),
            ("Y", "Y", ""),
            ("Z", "Z", ""),
            ("-X", "-X", ""),
            ("-Y", "-Y", ""),
            ("-Z", "-Z", "")
        ],
        default="Z"
    )

    mesh_export_coord_forward: EnumProperty(
        name="前向轴",
        description="导出网格的前向轴",
        items=[
            ("X", "X", ""),
            ("Y", "Y", ""),
            ("Z", "Z", ""),
            ("-X", "-X", ""),
            ("-Y", "-Y", ""),
            ("-Z", "-Z", "")
        ],
        default="X"
    )

    mesh_export_smoothing: EnumProperty(
        name="平滑",
        description="导出网格的平滑方法",
        items=[
            ("OFF", "关闭", "仅导出法线而不写入边缘或面平滑数据"),
            ("FACE", "面", "写入面平滑"),
            ("EDGE", "边", "写入边平滑"),
        ],
        default="FACE"
    )

    # Zero location property
    mesh_export_zero_location: BoolProperty(
        name="零位置",
        description="在导出前将对象副本的位置归零",
        default=True
    )

    # Triangulate properties
    mesh_export_tri: BoolProperty(
        name="三角化面",
        description="在副本上将所有面转换为三角形",
        default=True
    )

    # Triangulate method property
    mesh_export_tri_method: EnumProperty(
        name="方法",
        description="用于三角化四边形的方法",
        items=[
                ("BEAUTY", "美观", 
                 "使用最佳外观的结果进行三角化"),
                ("FIXED", "固定", 
                 "从第一个顶点到第三个顶点分割四边形"),
                ("FIXED_ALTERNATE", "固定交替", 
                 "从第二个顶点到第四个顶点分割四边形"),
                ("SHORTEST_DIAGONAL", "最短对角线", 
                 "沿最短对角线分割四边形")
            ],
        default="BEAUTY"
    )

    # Keep normals property
    mesh_export_keep_normals: BoolProperty(
        name="保持法线",
        description="在三角化过程中保留法线向量",
        default=True
    )

    # Prefix and suffix properties
    mesh_export_prefix: StringProperty(
        name="前缀",
        description="导出文件名的前缀",
        default=""
    )

    mesh_export_suffix: StringProperty(
        name="后缀",
        description="导出文件名的后缀",
        default=""
    )

    # LOD properties
    mesh_export_lod: BoolProperty(
        name="生成LOD",
        description="使用Decimate生成额外的LOD（修改副本）",
        default=False
    )

    # LOD count property
    mesh_export_lod_count: IntProperty(
        name="额外LOD数量",
        description="生成多少额外的LOD（LOD1到LOD4）",
        default=4, min=1, max=4, # 最多4个，因为有4个比率属性
    )

    # LOD symmetry property
    mesh_export_lod_symmetry: BoolProperty(
        name="对称",
        description="为LOD生成使用对称性",
        default=False
    )

    # LOD symmetry axis property
    mesh_export_lod_symmetry_axis: EnumProperty(
        name="对称轴",
        description="LOD生成的对称轴",
        items=[
            ("X", "X", "X轴"),
            ("Y", "Y", "Y轴"),
            ("Z", "Z", "Z轴")
        ],
        default="X"
    )

    # LOD type property
    mesh_export_lod_type: EnumProperty(
        name="简化类型",
        description="用于生成LOD的简化类型",
        items=[
            ("COLLAPSE", "折叠", "折叠边（比率）"),
        ],
        default="COLLAPSE",
    )

    # Material export property
    mesh_export_materials: BoolProperty(
        name="导出材质",
        description="与网格一起导出材质",
        default=True
    )
    
    # LOD ratio properties
    mesh_export_lod_ratio_01: FloatProperty(
        name="LOD1比率", 
        description="LOD 1的简化因子",
        default=0.75, min=0.0, max=1.0, subtype="FACTOR"
    )
    mesh_export_lod_ratio_02: FloatProperty(
        name="LOD2比率", 
        description="LOD 2的简化因子",
        default=0.50, min=0.0, max=1.0, subtype="FACTOR"
    )
    mesh_export_lod_ratio_03: FloatProperty(
        name="LOD3比率", 
        description="LOD 3的简化因子",
        default=0.25, min=0.0, max=1.0, subtype="FACTOR"
    )
    mesh_export_lod_ratio_04: FloatProperty(
        name="LOD4比率", 
        description="LOD 4的简化因子",
        default=0.10, min=0.0, max=1.0, subtype="FACTOR"
    )


def register_properties():
    """注册属性组并创建Scene属性"""
    try:
        bpy.utils.register_class(MeshExporterSettings)
        bpy.types.Scene.mesh_exporter = PointerProperty(
            type=MeshExporterSettings)
        # 验证
        test = bpy.types.Scene.bl_rna.properties.get("mesh_exporter")
        if test:
            logger.info(f"成功注册mesh_exporter: {test}")
        else:
            logger.error("注册mesh_exporter属性失败")
    except Exception as e:
        logger.error(f"注册属性时出错: {e}")


def unregister_properties():
    """注销属性组并移除Scene属性"""
    if hasattr(bpy.types.Scene, "mesh_exporter"):
        delattr(bpy.types.Scene, "mesh_exporter")
    try:
        bpy.utils.unregister_class(MeshExporterSettings)
    except Exception as e:
        logger.error(f"注销属性时出错: {e}")