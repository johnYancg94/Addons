# coding: utf-8
import bpy
import importlib

# Import all submodules
from . import operators
from . import panels

# Reload logic
def reload_submodules():
    importlib.reload(operators)
    importlib.reload(panels)
    # Delayed import of utils to avoid circular imports
    from . import utils
    importlib.reload(utils)

# Registration
classes = (
    # Add any classes from this __init__.py if needed
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    operators.register()
    panels.register()

def unregister():
    panels.unregister()
    operators.unregister()
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)