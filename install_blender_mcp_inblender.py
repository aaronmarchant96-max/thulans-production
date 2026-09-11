"""
Install and enable the blender_mcp addon from within running Blender.
Execute this in Blender's Text Editor (Run Script), or via:
  bpy.exec_expression(open('this_file.py').read())
"""
import bpy
import zipfile
import os
import sys

# Path to the addon zip
ADDON_ZIP = "/tmp/blender_mcp_addon.zip"
ADDONS_DIR = bpy.utils.user_resource('SCRIPTS', path="addons")

os.makedirs(ADDONS_DIR, exist_ok=True)

# Extract the addon zip
with zipfile.ZipFile(ADDON_ZIP, 'r') as zf:
    zf.extractall(ADDONS_DIR)
    print(f"[blender-mcp] Extracted to {ADDONS_DIR}")

# Refresh addon list and enable
bpy.ops.preferences.addon_refresh()

# Enable the addon
bpy.ops.preferences.addon_enable(module="blender_mcp")

# Save user prefs
bpy.ops.wm.save_userpref()

print("[blender-mcp] ✓ Addon enabled. Open the N-panel (N key in 3D Viewport) > 'BlenderMCP' tab > click Start Server.")
