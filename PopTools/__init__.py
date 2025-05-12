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

# --- Module Imports --- 
# Import all modules
try:
    from .modules.exporter import register as register_exporter
    from .modules.exporter import unregister as unregister_exporter
except ImportError:
    print("Exporter module not found or could not be imported")
    register_exporter = lambda: None
    unregister_exporter = lambda: None

# Import ReTex module
try:
    from .modules.retex import register as register_retex
    from .modules.retex import unregister as unregister_retex
except ImportError:
    print("ReTex module not found or could not be imported")
    register_retex = lambda: None
    unregister_retex = lambda: None

def register():
    """Registers all addon classes and properties."""
    # Create modules directory if it doesn't exist
    os.makedirs(modules_dir, exist_ok=True)
    os.makedirs(os.path.join(modules_dir, "exporter"), exist_ok=True)
    os.makedirs(os.path.join(modules_dir, "retex"), exist_ok=True)
    
    # Register exporter module
    try:
        register_exporter()
    except Exception as e:
        print(f"Error registering exporter module: {e}")
    
    # Register ReTex module
    try:
        register_retex()
    except Exception as e:
        print(f"Error registering ReTex module: {e}")
    
    print(f"Registered {bl_info['name']} Addon")

def unregister():
    """Unregisters all addon classes and properties."""
    # Unregister in reverse order
    
    # Unregister ReTex module first (reverse order)
    try:
        unregister_retex()
    except Exception as e:
        print(f"Error unregistering ReTex module: {e}")
    
    # Unregister exporter module
    try:
        unregister_exporter()
    except Exception as e:
        print(f"Error unregistering exporter module: {e}")
    
    print(f"Unregistered {bl_info['name']} Addon")

# For running the script directly
if __name__ == "__main__":
    register()