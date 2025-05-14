import bpy
from bpy.types import Panel
from .properties import VTBB_Properties
from .operators import VTBB_OT_CreateEmptiesForBones, VTBB_OT_BindEmptiesToVertices


class VTBB_PT_MainPanel(Panel):
    """创建主面板"""
    bl_label = "Vertex to Bone Baker"
    bl_idname = "VTBB_PT_MainPanel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'PopTools'
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        
        # 添加目标网格选择
        layout.prop(scene.vtbb_props, "target_mesh")
        
        # 添加操作按钮
        layout.operator(VTBB_OT_CreateEmptiesForBones.bl_idname)
        layout.operator(VTBB_OT_BindEmptiesToVertices.bl_idname)