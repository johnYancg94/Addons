# PopTools 插件

## 概述
PopTools是一个强大的Blender工具集插件，整合了多个实用工具，包括批量网格导出器和ReTex纹理工具。

## 当前状态
目前已经完成了基础框架的搭建，但还需要完成以下工作：

## 完成整合的步骤

### 1. 完成导出模块的迁移
已经创建了以下文件：
- `__init__.py` - 主插件文件，负责模块的注册和卸载
- `modules/exporter/__init__.py` - 导出模块的初始化文件
- `modules/exporter/properties.py` - 导出模块的属性定义

还需要创建以下文件：
- `modules/exporter/operators.py` - 从EasyMesh Batch Exporter迁移操作符代码
- `modules/exporter/panels.py` - 从EasyMesh Batch Exporter迁移面板代码
- `modules/exporter/indicators.py` - 从EasyMesh Batch Exporter迁移导出指示器代码

### 2. 修改面板结构
需要修改面板代码，使其显示在PopTools选项卡下，而不是原来的Exporter选项卡。

```python
# 原始代码
class MESH_PT_exporter_panel(Panel):
    bl_label = "EasyMesh Batch Exporter"
    bl_idname = "MESH_PT_exporter_panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Exporter" # 需要修改为 "PopTools"
```

### 3. 整合ReTex功能
创建ReTex模块的结构：
- `modules/retex/__init__.py`
- `modules/retex/properties.py`
- `modules/retex/operators.py`
- `modules/retex/panels.py`

### 4. 文件编码和中文支持
所有文件都应使用UTF-8编码，以确保中文注释不会出现乱码。已经在properties.py中将UI元素翻译为中文。

### 5. 测试和调试
完成代码迁移后，需要测试插件的功能，确保所有功能正常工作。

## 文件结构
完成后的插件结构应如下：

```
PopTools/
├── __init__.py
├── README.md
├── modules/
│   ├── exporter/
│   │   ├── __init__.py
│   │   ├── properties.py
│   │   ├── operators.py
│   │   ├── panels.py
│   │   └── indicators.py
│   └── retex/
│       ├── __init__.py
│       ├── properties.py
│       ├── operators.py
│       └── panels.py
```

## 注意事项
1. 确保所有导入路径正确，特别是在从原始插件迁移代码时
2. 保持模块化结构，便于后续添加更多工具
3. 使用UTF-8编码，确保中文显示正常
4. 在Blender 4.2中测试所有功能
