# -*- coding: utf-8 -*-
"""
PopTools Addon: A collection of useful tools for Blender.

This addon combines multiple tools including:
- Mesh Exporter: Batch export meshes with LOD generation
- ReTex: Texture management tools (placeholder for future integration)
"""

bl_info = {
    "name": "PopTools",
    "author": "Muton & Claude3.7 & Gemini0506",
    "version": (2, 0, 0),
    "blender": (4, 2, 0),
    "location": "View3D > Sidebar > PopTools Tab",
    "description": "A collection of useful tools including Batch Mesh Exporter and ReTex.",
    "warning": "",
    "doc_url": "",
    "category": "Object",
}

import bpy
import importlib
import os
import sys

# Add modules directory to path for imports
modules_dir = os.path.join(os.path.dirname(__file__), "modules")
if modules_dir not in sys.path:
    sys.path.append(modules_dir)

# --- Module Imports will be handled dynamically in register/unregister ---

def register():
    """Registers all addon classes and properties."""
    # Create modules directory if it doesn't exist
    os.makedirs(modules_dir, exist_ok=True)
    os.makedirs(os.path.join(modules_dir, "exporter"), exist_ok=True)
    os.makedirs(os.path.join(modules_dir, "retex"), exist_ok=True)

    # --- Dynamic Module Imports and Reloading ---
    # Exporter module
    try:
        if ".modules.exporter" in sys.modules and "bpy" in locals():
            importlib.reload(sys.modules[".modules.exporter"])
            if ".modules.exporter.properties" in sys.modules: importlib.reload(sys.modules[".modules.exporter.properties"])
            if ".modules.exporter.operators" in sys.modules: importlib.reload(sys.modules[".modules.exporter.operators"])
            if ".modules.exporter.panels" in sys.modules: importlib.reload(sys.modules[".modules.exporter.panels"])
            if ".modules.exporter.indicators" in sys.modules: importlib.reload(sys.modules[".modules.exporter.indicators"])

        from .modules.exporter import register as register_exporter_func
        register_exporter_func()
    except ImportError as e:
        print(f"Exporter module not found or could not be imported during register: {e}")
    except Exception as e:
        print(f"Error registering exporter module: {e}")

    # ReTex module
    try:
        if ".modules.retex" in sys.modules and "bpy" in locals():
            importlib.reload(sys.modules[".modules.retex"])
            if ".modules.retex.properties" in sys.modules: importlib.reload(sys.modules[".modules.retex.properties"])
            if ".modules.retex.operators" in sys.modules: importlib.reload(sys.modules[".modules.retex.operators"])
            if ".modules.retex.panels" in sys.modules: importlib.reload(sys.modules[".modules.retex.panels"])

        from .modules.retex import register as register_retex_func
        register_retex_func()
    except ImportError as e:
        print(f"ReTex module not found or could not be imported during register: {e}")
    except Exception as e:
        print(f"Error registering ReTex module: {e}")

    print(f"Registered {bl_info['name']} Addon")

def unregister():
    """Unregisters all addon classes and properties."""
    # Unregister in reverse order

    # ReTex module
    try:
        from .modules.retex import unregister as unregister_retex_func
        unregister_retex_func()
    except ImportError:
        print("ReTex module (or its unregister function) not found during unregister.")
    except Exception as e:
        print(f"Error unregistering ReTex module: {e}")

    # Exporter module
    try:
        from .modules.exporter import unregister as unregister_exporter_func
        unregister_exporter_func()
    except ImportError:
        print("Exporter module (or its unregister function) not found during unregister.")
    except Exception as e:
        print(f"Error unregistering exporter module: {e}")

    print(f"Unregistered {bl_info['name']} Addon")

# For running the script directly
if __name__ == "__main__":
    register()