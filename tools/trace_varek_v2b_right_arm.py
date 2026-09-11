#!/usr/bin/env python3
"""Read-only matrix trace for the failed character-right V2B arm."""

from __future__ import annotations

import json
from pathlib import Path

import bpy
from mathutils import Vector


OUTPUT = Path("/home/aaron/animation/thulans-production/evidence/varek-v2b4-rig/right-arm-matrix-trace.json")
ARMATURE = "Varek_Original_Rig"
FRAMES = (1, 20)
OBJECTS = ("Forearm_R_OUTER", "Wrist_Bearing_R", "Manipulator_Palm_R")
BONES = ("upper_arm.R", "forearm.R", "hand.R")


def matrix_rows(matrix):
    return [[float(value) for value in row] for row in matrix]


def vector_values(vector):
    return [float(value) for value in vector]


def evaluated_bounds_center(obj, depsgraph):
    evaluated = obj.evaluated_get(depsgraph)
    mesh = evaluated.to_mesh()
    try:
        points = [evaluated.matrix_world @ vertex.co for vertex in mesh.vertices]
        low = Vector((min(p.x for p in points), min(p.y for p in points), min(p.z for p in points)))
        high = Vector((max(p.x for p in points), max(p.y for p in points), max(p.z for p in points)))
        return vector_values((low + high) / 2), vector_values(low), vector_values(high)
    finally:
        evaluated.to_mesh_clear()


def deform_world_matrix(rig, bone_name):
    pose = rig.pose.bones[bone_name]
    rest = rig.data.bones[bone_name]
    return rig.matrix_world @ pose.matrix @ rest.matrix_local.inverted() @ rig.matrix_world.inverted()


def object_record(obj, depsgraph):
    center, low, high = evaluated_bounds_center(obj, depsgraph)
    return {
        "matrix_world": matrix_rows(obj.matrix_world),
        "matrix_parent_inverse": matrix_rows(obj.matrix_parent_inverse),
        "parent": obj.parent.name if obj.parent else None,
        "parent_type": obj.parent_type,
        "parent_bone": obj.parent_bone,
        "location": vector_values(obj.location),
        "rotation_euler": vector_values(obj.rotation_euler),
        "scale": vector_values(obj.scale),
        "origin_world": vector_values(obj.matrix_world.translation),
        "evaluated_bounds_center_world": center,
        "evaluated_bounds_low_world": low,
        "evaluated_bounds_high_world": high,
        "rigid_driver_bone": obj.get("rigid_driver_bone"),
        "vertex_groups": [group.name for group in obj.vertex_groups],
        "modifiers": [
            {
                "name": modifier.name,
                "type": modifier.type,
                "object": modifier.object.name if getattr(modifier, "object", None) else None,
            }
            for modifier in obj.modifiers
        ],
    }


def main():
    if not bpy.data.filepath:
        raise RuntimeError("open the failed V2B4 blend before tracing")
    blend = Path(bpy.data.filepath)
    rig = bpy.data.objects[ARMATURE]
    record = {
        "schema_version": "1.0",
        "claim_class": "OBSERVED",
        "gate": "V2B_RIGHT_ARM_MATRIX_TRACE",
        "source_blend": str(blend),
        "read_only": True,
        "armature_matrix_world": matrix_rows(rig.matrix_world),
        "frames": {},
    }
    for frame in FRAMES:
        bpy.context.scene.frame_set(frame)
        bpy.context.view_layer.update()
        depsgraph = bpy.context.evaluated_depsgraph_get()
        bones = {}
        for name in BONES:
            rest = rig.data.bones[name]
            pose = rig.pose.bones[name]
            bones[name] = {
                "rest_matrix_local": matrix_rows(rest.matrix_local),
                "pose_matrix": matrix_rows(pose.matrix),
                "matrix_basis": matrix_rows(pose.matrix_basis),
                "head_world": vector_values(rig.matrix_world @ pose.head),
                "tail_world": vector_values(rig.matrix_world @ pose.tail),
                "deform_world_matrix": matrix_rows(deform_world_matrix(rig, name)),
            }

        wrist_rest_world = rig.matrix_world @ rig.data.bones["hand.R"].head_local
        forearm_socket = deform_world_matrix(rig, "forearm.R") @ wrist_rest_world
        hand_socket = deform_world_matrix(rig, "hand.R") @ wrist_rest_world
        elbow_rest_world = rig.matrix_world @ rig.data.bones["forearm.R"].head_local
        upper_socket = deform_world_matrix(rig, "upper_arm.R") @ elbow_rest_world
        forearm_proximal = deform_world_matrix(rig, "forearm.R") @ elbow_rest_world
        record["frames"][str(frame)] = {
            "bones": bones,
            "objects": {name: object_record(bpy.data.objects[name], depsgraph) for name in OBJECTS},
            "interfaces": {
                "wrist_rest_world": vector_values(wrist_rest_world),
                "forearm_distal_socket_world": vector_values(forearm_socket),
                "hand_proximal_socket_world": vector_values(hand_socket),
                "wrist_gap_m": float((forearm_socket - hand_socket).length),
                "upper_arm_distal_socket_world": vector_values(upper_socket),
                "forearm_proximal_socket_world": vector_values(forearm_proximal),
                "elbow_gap_m": float((upper_socket - forearm_proximal).length),
            },
        }
    record["diagnosis_inputs"] = {
        "wrist_gap_delta_m": record["frames"]["20"]["interfaces"]["wrist_gap_m"] - record["frames"]["1"]["interfaces"]["wrist_gap_m"],
        "elbow_gap_delta_m": record["frames"]["20"]["interfaces"]["elbow_gap_m"] - record["frames"]["1"]["interfaces"]["elbow_gap_m"],
    }
    OUTPUT.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "frame_1_wrist_gap_m": record["frames"]["1"]["interfaces"]["wrist_gap_m"],
        "frame_20_wrist_gap_m": record["frames"]["20"]["interfaces"]["wrist_gap_m"],
        "frame_1_elbow_gap_m": record["frames"]["1"]["interfaces"]["elbow_gap_m"],
        "frame_20_elbow_gap_m": record["frames"]["20"]["interfaces"]["elbow_gap_m"],
        "output": str(OUTPUT),
    }, indent=2))


if __name__ == "__main__":
    main()
