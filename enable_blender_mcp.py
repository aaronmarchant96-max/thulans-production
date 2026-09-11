"""
Enable the blender_mcp addon and start the MCP socket server.
Run this in Blender headlessly to register the addon,
then Blender GUI should have the N-panel MCP tab visible.
"""
import bpy
import addon_utils

# Enable the addon
addon_utils.enable("blender_mcp", default_set=True, persistent=True)

# Save user preferences so it stays enabled across restarts
bpy.ops.wm.save_userpref()
print("[blender-mcp] Addon enabled and preferences saved.")
