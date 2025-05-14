import bpy
from bpy.types import PropertyGroup
from bpy.props import PointerProperty


class VTBB_Properties(PropertyGroup):
    """存储插件的属性"""
    target_mesh: PointerProperty(
        name="目标网格",
        description="选择要绑定到的网格对象",
        type=bpy.types.Object,
        poll=lambda self, obj: obj.type == 'MESH'
    )