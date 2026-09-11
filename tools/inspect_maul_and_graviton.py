import bpy
from pathlib import Path
from mathutils import Vector

def inspect_maul_and_graviton():
    root = Path("/home/aaron/animation/thulans-production")
    v52 = root / "blender/candidates/varek-v52-graviton.blend"
    bpy.ops.wm.open_mainfile(filepath=str(v52))
    
    print("\n=== FAULT MAUL INSPECTION ===")
    maul_parts = [o for o in bpy.data.objects if any(k in o.name.lower() for k in ["maul", "hammer", "haft", "shaft", "head"])]
    for o in maul_parts:
        if o.type == 'MESH':
            dim = o.dimensions
            print(f"Part '{o.name}': Dim X={dim.x:.4f}, Y={dim.y:.4f}, Z={dim.z:.4f}")
            
    print("\n=== GRAVITON MANIPULATOR / RIGHT ARM ===")
    grav_parts = [o for o in bpy.data.objects if any(k in o.name.lower() for k in ["talon", "graviton", "induction", "ring", "conduit", "vane"])]
    for o in grav_parts:
        if o.type == 'MESH':
            dim = o.dimensions
            print(f"Part '{o.name}': Dim X={dim.x:.4f}, Y={dim.y:.4f}, Z={dim.z:.4f} | Center: {o.matrix_world.translation}")

    print("\n=== FOREARM CUFFS & WRIST COUPLINGS ===")
    cuffs = [o for o in bpy.data.objects if any(k in o.name.lower() for k in ["cuff", "coupling", "forearm", "wrist"])]
    for o in cuffs:
        if o.type == 'MESH':
            dim = o.dimensions
            print(f"Part '{o.name}': Dim X={dim.x:.4f}, Y={dim.y:.4f}, Z={dim.z:.4f} | Center: {o.matrix_world.translation}")

if __name__ == "__main__":
    inspect_maul_and_graviton()
