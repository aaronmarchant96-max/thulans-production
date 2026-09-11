import bpy
from pathlib import Path
from mathutils import Vector

def inspect_file(filepath):
    print(f"\n=======================================================")
    print(f"INSPECTING: {filepath}")
    print(f"=======================================================")
    bpy.ops.wm.open_mainfile(filepath=str(filepath))
    
    print("\n--- RELEVANT OBJECTS & BOUNDS ---")
    keywords = ["forearm", "wrist", "hand", "palm", "finger", "thumb", "talon", "ring", "maul", "hammer", "cuff", "gauntlet"]
    for obj in bpy.data.objects:
        name_lower = obj.name.lower()
        if any(k in name_lower for k in keywords) or obj.type == 'ARMATURE':
            if obj.type == 'MESH':
                bbox = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
                min_x = min(v.x for v in bbox)
                max_x = max(v.x for v in bbox)
                min_y = min(v.y for v in bbox)
                max_y = max(v.y for v in bbox)
                min_z = min(v.z for v in bbox)
                max_z = max(v.z for v in bbox)
                dim = obj.dimensions
                print(f"Mesh: '{obj.name}' | Parent: {obj.parent.name if obj.parent else 'None'}")
                print(f"  Dimensions: X={dim.x:.4f}, Y={dim.y:.4f}, Z={dim.z:.4f}")
                print(f"  Bounds World: X=[{min_x:.4f}, {max_x:.4f}], Y=[{min_y:.4f}, {max_y:.4f}], Z=[{min_z:.4f}, {max_z:.4f}]")
                print(f"  Center: {obj.matrix_world.translation}")
                
            elif obj.type == 'ARMATURE':
                print(f"Armature: '{obj.name}'")
                for bone in obj.data.bones:
                    b_name = bone.name.lower()
                    if any(k in b_name for k in keywords):
                        print(f"  Bone: '{bone.name}' | Parent: {bone.parent.name if bone.parent else 'None'}")
                        print(f"    Head: ({bone.head.x:.4f}, {bone.head.y:.4f}, {bone.head.z:.4f})")
                        print(f"    Tail: ({bone.tail.x:.4f}, {bone.tail.y:.4f}, {bone.tail.z:.4f}) | Length: {bone.length:.4f}")

if __name__ == "__main__":
    root = Path("/home/aaron/animation/thulans-production")
    v51 = root / "blender/candidates/varek-v51-functional.blend"
    v52 = root / "blender/candidates/varek-v52-graviton.blend"
    if v51.exists():
        inspect_file(v51)
    if v52.exists():
        inspect_file(v52)
