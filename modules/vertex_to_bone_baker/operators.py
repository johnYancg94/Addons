import bpy
from bpy.types import Operator


class VTBB_OT_CreateEmptiesForBones(Operator):
    """为每根骨骼创建对应的空物体并设置约束"""
    bl_idname = "vtbb.create_empties_for_bones"
    bl_label = "创建空物体并绑定到骨骼"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        # 获取当前选中的骨架对象
        armature = context.active_object
        
        if not armature or armature.type != 'ARMATURE':
            self.report({'ERROR'}, "请先选择一个骨架对象")
            return {'CANCELLED'}
        
        # 获取骨架中的所有骨骼
        bones = armature.data.bones
        
        # 创建一个空物体集合来存放所有创建的空物体
        if "VTBB_Empties" not in bpy.data.collections:
            empty_collection = bpy.data.collections.new("VTBB_Empties")
            bpy.context.scene.collection.children.link(empty_collection)
        else:
            empty_collection = bpy.data.collections["VTBB_Empties"]
        
        # 为每根骨骼创建一个空物体
        created_empties = []
        for bone in bones:
            # 创建空物体名称
            empty_name = f"empty_{bone.name}"
            
            # 检查是否已存在同名空物体
            if empty_name in bpy.data.objects:
                empty = bpy.data.objects[empty_name]
            else:
                # 创建一个箭头型空物体
                empty = bpy.data.objects.new(empty_name, None)
                empty.empty_display_type = 'ARROWS'
                empty.empty_display_size = 0.1
                
                # 将空物体添加到集合中
                empty_collection.objects.link(empty)
            
            # 记录创建的空物体
            created_empties.append(empty)
            
            # 设置空物体的位置为骨骼的头部位置
            # 需要考虑骨架的世界变换
            world_matrix = armature.matrix_world
            empty.location = world_matrix @ bone.head_local
            
            # 添加Copy Transforms约束到空物体
            constraint_name = "Copy Bone Transform"
            
            # 检查并移除已存在的同名约束
            for constraint in empty.constraints:
                if constraint.name == constraint_name:
                    empty.constraints.remove(constraint)
            
            constraint = empty.constraints.new('COPY_TRANSFORMS')
            constraint.name = constraint_name
            constraint.target = armature
            constraint.subtarget = bone.name
        
        # 应用Visual Transform并移除约束
        for empty in created_empties:
            # 切换到物体模式
            bpy.ops.object.mode_set(mode='OBJECT')
            
            # 取消选择所有对象
            bpy.ops.object.select_all(action='DESELECT')
            
            # 选择当前空物体
            empty.select_set(True)
            context.view_layer.objects.active = empty
            
            # 应用Visual Transform
            bpy.ops.object.visual_transform_apply()
            
            # 移除Copy Transforms约束
            for constraint in empty.constraints:
                if constraint.name == "Copy Bone Transform":
                    empty.constraints.remove(constraint)
        
        # 为每根骨骼添加Copy Transforms约束到对应的空物体
        # 切换到姿态模式
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.select_all(action='DESELECT')
        armature.select_set(True)
        context.view_layer.objects.active = armature
        bpy.ops.object.mode_set(mode='POSE')
        
        for bone in armature.pose.bones:
            empty_name = f"empty_{bone.name}"
            if empty_name in bpy.data.objects:
                empty = bpy.data.objects[empty_name]
                
                # 检查并移除已存在的同名约束
                constraint_name = "Copy Empty Transform"
                for constraint in bone.constraints:
                    if constraint.name == constraint_name:
                        bone.constraints.remove(constraint)
                
                # 添加Copy Transforms约束
                constraint = bone.constraints.new('COPY_TRANSFORMS')
                constraint.name = constraint_name
                constraint.target = empty
        
        # 切换回物体模式
        bpy.ops.object.mode_set(mode='OBJECT')
        
        self.report({'INFO'}, f"成功为{len(bones)}根骨骼创建了空物体并设置了约束")
        return {'FINISHED'}


class VTBB_OT_BindEmptiesToVertices(Operator):
    """将选中的空物体绑定到指定网格的顶点上"""
    bl_idname = "vtbb.bind_empties_to_vertices"
    bl_label = "绑定空物体到顶点"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        # 获取当前选中的空物体
        selected_empties = [obj for obj in context.selected_objects if obj.type == 'EMPTY']
        
        if not selected_empties:
            self.report({'ERROR'}, "请先选择至少一个空物体")
            return {'CANCELLED'}
        
        # 获取用户指定的目标网格对象
        target_mesh = context.scene.vtbb_props.target_mesh
        
        if not target_mesh:
            self.report({'ERROR'}, "请先选择一个目标网格对象")
            return {'CANCELLED'}
        
        if target_mesh.type != 'MESH':
            self.report({'ERROR'}, "选择的对象不是网格对象")
            return {'CANCELLED'}
        
        # 为每个选中的空物体找到最近的三个顶点并执行绑定
        for empty in selected_empties:
            # 使用用户指定的网格对象
            closest_mesh = target_mesh
            
            if closest_mesh:
                # 获取网格数据
                mesh_data = closest_mesh.data
                world_matrix = closest_mesh.matrix_world
                
                # 计算空物体到每个顶点的距离
                distances = []
                for i, vertex in enumerate(mesh_data.vertices):
                    # 将顶点坐标转换到世界空间
                    vertex_world = world_matrix @ vertex.co
                    # 计算距离
                    distance = (empty.matrix_world.translation - vertex_world).length
                    distances.append((i, distance))
                
                # 按距离排序并获取最近的三个顶点
                distances.sort(key=lambda x: x[1])
                closest_vertices = [distances[i][0] for i in range(min(3, len(distances)))]
                
                # 执行MakeVertexParent操作
                # 首先取消选择所有对象
                bpy.ops.object.select_all(action='DESELECT')
                
                # 选择网格对象并设置为活动对象
                closest_mesh.select_set(True)
                context.view_layer.objects.active = closest_mesh
                
                # 进入编辑模式
                bpy.ops.object.mode_set(mode='EDIT')
                
                # 取消选择所有顶点
                bpy.ops.mesh.select_all(action='DESELECT')
                
                # 选择最近的三个顶点
                bpy.ops.object.mode_set(mode='OBJECT')
                for vertex_index in closest_vertices:
                    mesh_data.vertices[vertex_index].select = True
                
                # 返回编辑模式
                bpy.ops.object.mode_set(mode='EDIT')
                
                # 选择空物体
                bpy.ops.object.mode_set(mode='OBJECT')
                empty.select_set(True)
                
                # 执行MakeVertexParent操作
                bpy.ops.object.parent_set(type='VERTEX_TRI')
        
        self.report({'INFO'}, f"成功将{len(selected_empties)}个空物体绑定到最近的顶点上")
        return {'FINISHED'}