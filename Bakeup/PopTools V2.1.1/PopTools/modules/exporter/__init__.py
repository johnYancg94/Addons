# -*- coding: utf-8 -*-
"""
Mesh Exporter module for PopTools

This module provides batch mesh exporting functionality with support for
multiple formats, LOD generation, and export indicators.
"""

import bpy
import logging

# --- Setup Logger ---
logger = logging.getLogger(__name__)
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter("%(name)s:%(levelname)s: %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)  # Default level

# Import submodules
from . import properties
from . import operators
from . import panels
from . import indicators

# Registration
classes = (
    *operators.classes,
    *panels.classes,
    # indicators registers its own classes/timer
)


def register():
    """Register all exporter module components"""
    logger.info("Begin exporter module registration.")
    # 1. Properties FIRST
    properties.register_properties()
    logger.info("Exporter properties registered.")

    # 2. Other Classes (Operators, Panels)
    for cls in classes:
        bpy.utils.register_class(cls)
    logger.info("Exporter panel/operator classes registered.")

    # 3. Indicators
    indicators.register()
    logger.info("Export indicators registered.")
    logger.info("Exporter module registration complete.")


def unregister():
    """Unregister all exporter module components"""
    logger.info("Begin exporter module unregistration.")
    # Unregister in REVERSE order

    # 1. Indicators
    indicators.unregister()
    logger.info("Export indicators unregistered.")

    # 2. Other Classes
    for cls in reversed(classes):
        try:
            bpy.utils.unregister_class(cls)
        except RuntimeError as e:
            logger.error(f"Couldn't unregister {cls}: {e}")
    logger.info("Exporter panel/operator classes unregistered.")

    # 3. Properties LAST
    properties.unregister_properties()
    logger.info("Exporter properties unregistered.")
    logger.info("Exporter module unregistration complete.")