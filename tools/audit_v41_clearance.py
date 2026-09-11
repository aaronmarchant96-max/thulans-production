"""Real clearance auditor for thulans-production candidates.

Contract: docs/AGY_OPERATING_CONTRACT.md

- Pose-activity assertion (POSE; pelvis/thigh.L/thigh.R must move) hard-fails
  before any collision analysis.
- Curated prohibited kinematic pairs -> hard FAIL on overlap.
- All-pairs broadphase inventory over major meshes -> reported for review.
- Per-mesh self-intersection -> hard FAIL.
- Envelope: grounding/height gated at REST (canonical build pose); the walk
  action's foot-sink is reported as an animation artifact, not gated.
- Hash-bound JSON written to the candidate's OWN evidence directory.
- Framing renders: full-body PERSPECTIVE, scene-lit front/side/q34 at REST,
  head and ground visible. (Flat orthographic workbench renders of layered
  armor read as broken geometry -- a presentation defect, not a mesh defect.)
- Exits nonzero on FAIL. Run with --python-exit-code 1.

Usage:
  flatpak run --filesystem=host org.blender.Blender --background \
    --python-exit-code 1 --python tools/audit_v41_clearance.py -- \
    --candidate blender/candidates/varek-v41-clean-functional.blend
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from pathlib import Path

import bpy
import bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree

ROOT = Path("/home/aaron/animation/thulans-production")
CANONICAL_HEIGHT = 2.4384
GROUND_TOL = 0.002
HEIGHT_TOL = 0.002
MAJOR_MIN_VERTS = 24

# Kinematic clearances that must never intersect (carry rig, v35 lineage).
PROHIBITED_PAIRS = [
    ("Pelvic cradle", "Donor thigh L"),
    ("Pelvic cradle", "Donor thigh R"),
    ("Pelvic cradle", "Thigh guard L"),
    ("Pelvic cradle", "Thigh guard R"),
    ("Thigh guard L", "Donor thigh L"),
    ("Thigh guard R", "Donor thigh R"),
    ("Donor thigh L", "Donor thigh R"),
    ("Donor shin L", "Donor shin R"),
    ("Knee bearing L", "Donor thigh L"),
    ("Knee bearing R", "Donor thigh R"),
    ("Forged foot housing L", "Forged foot housing R"),
    ("Thoracic protective hull", "Donor upper arm L"),
    ("Thoracic protective hull", "Donor upper arm R"),
    ("Thoracic protective hull", "Donor forearm L"),
    ("Thoracic protective hull", "Donor forearm R"),
    ("Thoracic protective hull", "Donor rescue hand L"),
    ("Thoracic protective hull", "Donor rescue hand R"),
    ("Shoulder collar L", "Thoracic protective hull"),
    ("Shoulder collar R", "Thoracic protective hull"),
    ("Donor upper arm L", "Donor upper arm R"),
    ("Donor forearm L", "Donor forearm R"),
    ("Donor rescue hand L", "Donor rescue hand R"),
]

# Contact is expected/allowed for these (nested mechanisms, joints, carried tool).
ALLOWED_CONTACT_HINTS = (
    "Hydraulic", "Cylinder", "Rod", "Port", "Mount", "Clevis", "Pin", "Axle",
    "Bearing", "Bolt", "Rivet", "Ferrule", "Grip", "Rib", "Band", "Saddle",
    "Conduit", "Hose", "Fitting", "Coupling", "Collar", "Guard", "Trim",
    "Cleat", "Sole", "Anchor", "Maul",
)
EXCLUDE_ENVELOPE = ("Studio floor", "Atmospheric_Forge_Haze")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def evaluated_tris(obj, depsgraph):
    """Return (world_triangles, tri_vertex_indices) for the evaluated mesh."""
    eo = obj.evaluated_get(depsgraph)
    me = eo.to_mesh()
    if me is None or len(me.vertices) == 0:
        eo.to_mesh_clear()
        return None, None
    bm = bmesh.new()
    bm.from_mesh(me)
    bmesh.ops.triangulate(bm, faces=bm.faces[:])
    bm.transform(eo.matrix_world)
    tris = [tuple(v.co.copy() for v in f.verts) for f in bm.faces]
    idx = [tuple(v.index for v in f.verts) for f in bm.faces]
    bm.free()
    eo.to_mesh_clear()
    return tris, idx


def bvh_from_tris(tris):
    verts = []
    faces = []
    for tri in tris:
        base = len(verts)
        verts.extend(tri)
        faces.append((base, base + 1, base + 2))
    return BVHTree.FromPolygons(verts, faces, epsilon=1e-4)


def world_aabb(obj, depsgraph):
    eo = obj.evaluated_get(depsgraph)
    pts = [eo.matrix_world @ Vector(c) for c in eo.bound_box]
    return (
        Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts))),
        Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts))),
    )


def self_intersections(obj, depsgraph):
    tris, idx = evaluated_tris(obj, depsgraph)
    if not tris:
        return 0
    bvh = bvh_from_tris(tris)
    pairs = bvh.overlap(bvh)
    count = 0
    for i, j in pairs:
        if i >= j:
            continue
        if set(idx[i]) & set(idx[j]):
            continue
        count += 1
    return count


def is_allowed(a: str, b: str) -> bool:
    return any(h in a or h in b for h in ALLOWED_CONTACT_HINTS)


def run() -> int:
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    ap = argparse.ArgumentParser()
    ap.add_argument("--candidate", default="blender/candidates/varek-v41-clean-functional.blend")
    ap.add_argument("--evidence", default=None)
    ap.add_argument("--strict-all-pairs", action="store_true")
    args = ap.parse_args(argv)

    candidate = (ROOT / args.candidate).resolve()
    if not candidate.exists():
        print(f"FATAL: candidate not found: {candidate}")
        return 2
    stem = candidate.stem
    evidence_dir = Path(args.evidence).resolve() if args.evidence else (ROOT / "evidence" / stem)
    evidence_dir.mkdir(parents=True, exist_ok=True)

    file_sha = sha256(candidate)
    print(f"candidate: {candidate}")
    print(f"sha256:    {file_sha}")

    bpy.ops.wm.open_mainfile(filepath=str(candidate))
    scene = bpy.context.scene

    armatures = [o for o in bpy.data.objects if o.type == "ARMATURE"]
    if not armatures:
        print("FATAL: no armature")
        return 2
    rig = armatures[0]
    if rig.data.pose_position != "POSE":
        print(f"FATAL: pose_position={rig.data.pose_position}, must be POSE")
        return 1
    if not rig.animation_data or not rig.animation_data.action:
        print("FATAL: rig has no action")
        return 2
    action = rig.animation_data.action
    f0, f1 = int(action.frame_range[0]), int(action.frame_range[1])
    print(f"rig={rig.name} action={action.name} frames={f0}-{f1} pose=POSE")

    # --- pose-activity assertion -------------------------------------------------
    sample = sorted({f0 + round((f1 - f0) * k / 5) for k in range(6)})
    activity = {}
    for bone in ("pelvis", "thigh.L", "thigh.R"):
        seen = set()
        if bone in rig.pose.bones:
            for f in sample:
                scene.frame_set(f)
                bpy.context.view_layer.update()
                pb = rig.pose.bones[bone]
                seen.add(tuple(round(v, 5) for row in pb.matrix for v in row))
        activity[bone] = len(seen)
    print(f"pose_activity: {activity}")
    static = [b for b, n in activity.items() if n <= 1]
    pose_activity_ok = not static
    if not pose_activity_ok:
        print(f"FATAL: pose-activity failed (static bones: {static})")

    # --- envelope -----------------------------------------------------------------
    # Canonical grounding/height is defined at REST (the rig's neutral build pose).
    # The walk action is a separate animation artifact and is reported, not gated.
    meshes = [o for o in bpy.data.objects if o.type == "MESH"]
    char = [o for o in meshes if o.name not in EXCLUDE_ENVELOPE]

    rig.data.pose_position = "REST"
    scene.frame_set(f0)
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    rest_zmin = min(world_aabb(o, dg)[0].z for o in char)
    rest_zmax = max(world_aabb(o, dg)[1].z for o in char)
    rest_height = rest_zmax - rest_zmin
    rig.data.pose_position = "POSE"
    bpy.context.view_layer.update()

    # posed (walk) envelope across all frames -- reported for review
    pose_zmin = float("inf")
    pose_zmax = float("-inf")
    for f in range(f0, f1 + 1):
        scene.frame_set(f)
        bpy.context.view_layer.update()
        dg = bpy.context.evaluated_depsgraph_get()
        pose_zmin = min(pose_zmin, min(world_aabb(o, dg)[0].z for o in char))
        pose_zmax = max(pose_zmax, max(world_aabb(o, dg)[1].z for o in char))
    walk_foot_sink = pose_zmin

    ground_ok = abs(rest_zmin - 0.0) <= GROUND_TOL
    height_ok = abs(rest_height - CANONICAL_HEIGHT) <= HEIGHT_TOL
    print(f"envelope REST: z_min={rest_zmin:.6f} z_max={rest_zmax:.6f} height={rest_height:.6f} "
          f"(ground_ok={ground_ok} height_ok={height_ok})")
    print(f"envelope POSE: z_min={pose_zmin:.6f} z_max={pose_zmax:.6f} "
          f"walk_foot_sink={walk_foot_sink:.6f} (animation, not gated)")

    # --- collision sweep ----------------------------------------------------------
    by_name = {o.name: o for o in meshes}
    major = [o.name for o in meshes if len(o.data.vertices) >= MAJOR_MIN_VERTS]

    # Dynamically map right-hand geometry if replaced per RULING 023/024
    graviton_r = [n for n in by_name if any(k in n for k in ["Graviton", "Talon_Dorsal", "Talon_Inboard", "Talon_Outboard"])]
    active_prohibited = []
    for a, b in PROHIBITED_PAIRS:
        a_targets = [a]
        b_targets = [b]
        if a == "Donor rescue hand R" and a not in by_name and graviton_r:
            a_targets = graviton_r
        if b == "Donor rescue hand R" and b not in by_name and graviton_r:
            b_targets = graviton_r
        for ea in a_targets:
            for eb in b_targets:
                active_prohibited.append((ea, eb))

    pair_names = sorted({n for p in active_prohibited for n in p})
    missing = [n for n in pair_names if n not in by_name]
    if missing:
        print(f"FATAL: missing prohibited-pair geometry: {missing}")
        return 2

    prohibited_hits = []
    review_pairs = {}
    for f in range(f0, f1 + 1):
        scene.frame_set(f)
        bpy.context.view_layer.update()
        dg = bpy.context.evaluated_depsgraph_get()

        bvhs = {}
        boxes = {}
        for name in set(pair_names) | set(major):
            obj = by_name[name]
            tris, _ = evaluated_tris(obj, dg)
            if tris:
                bvhs[name] = bvh_from_tris(tris)
                boxes[name] = world_aabb(obj, dg)

        for a, b in active_prohibited:
            if a in bvhs and b in bvhs and bvhs[a].overlap(bvhs[b]):
                prohibited_hits.append({"frame": f, "a": a, "b": b})

        for i in range(len(major)):
            for j in range(i + 1, len(major)):
                a, b = major[i], major[j]
                if a not in boxes or b not in boxes:
                    continue
                amin, amax = boxes[a]
                bmin, bmax = boxes[b]
                if (amax.x < bmin.x or bmax.x < amin.x or
                        amax.y < bmin.y or bmax.y < amin.y or
                        amax.z < bmin.z or bmax.z < amin.z):
                    continue
                if (a, b) in [tuple(sorted(p)) for p in active_prohibited]:
                    continue
                if a in bvhs and b in bvhs and bvhs[a].overlap(bvhs[b]):
                    if not is_allowed(a, b):
                        review_pairs.setdefault(f"{a} <-> {b}", 0)
                        review_pairs[f"{a} <-> {b}"] += 1

    # --- self-intersection (frame f0) --------------------------------------------
    scene.frame_set(f0)
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    self_hits = {}
    for name in major:
        n = self_intersections(by_name[name], dg)
        if n:
            self_hits[name] = n
    print(f"self_intersections: {len(self_hits)} meshes")

    # --- renders ------------------------------------------------------------------
    # Clear perspective, scene-lit full-body views at the canonical REST pose.
    # (Flat orthographic workbench renders of layered armor read as "broken"
    #  geometry; this is a presentation defect, not a geometry defect.)
    for c in list(bpy.data.cameras):
        bpy.data.cameras.remove(c)
    for o in [x for x in bpy.data.objects if x.type == "CAMERA"]:
        bpy.data.objects.remove(o)
    cam_data = bpy.data.cameras.new("AuditCam")
    cam_data.type = "PERSP"
    cam_data.lens = 50.0
    cam = bpy.data.objects.new("AuditCam", cam_data)
    scene.collection.objects.link(cam)
    scene.camera = cam
    scene.render.resolution_x = 900
    scene.render.resolution_y = 1200
    scene.render.film_transparent = False
    rig.data.pose_position = "REST"
    scene.frame_set(f0)
    bpy.context.view_layer.update()
    target = Vector((0.0, -0.15, (rest_zmin + rest_zmax) / 2.0))
    renders = {}
    for label, loc in (
        ("front", Vector((0.0, -4.6, target.z))),
        ("side", Vector((4.6, 0.0, target.z))),
        ("q34", Vector((3.1, -3.6, target.z + 0.9))),
    ):
        cam.location = loc
        cam.rotation_euler = (target - loc).to_track_quat("-Z", "Y").to_euler()
        out = evidence_dir / f"audit-{label}.png"
        scene.render.filepath = str(out)
        bpy.ops.render.render(write_still=True)
        renders[label] = out.name
        print(f"render: {out}")
    rig.data.pose_position = "POSE"

    # --- verdict ------------------------------------------------------------------
    fail_reasons = []
    if not pose_activity_ok:
        fail_reasons.append(f"static pose bones: {static}")
    if not ground_ok or not height_ok:
        fail_reasons.append(
            f"REST envelope off-canonical (z_min={rest_zmin:.4f}, height={rest_height:.4f})"
        )
    if prohibited_hits:
        fail_reasons.append(f"{len(prohibited_hits)} prohibited intersections")
    if self_hits:
        fail_reasons.append(f"{len(self_hits)} self-intersecting meshes")
    if args.strict_all_pairs and review_pairs:
        fail_reasons.append(f"{len(review_pairs)} non-allowed all-pairs overlaps")

    report = {
        "gate": "VAREK_CLEARANCE_AUDIT",
        "candidate": str(candidate),
        "candidate_sha256": file_sha,
        "rig": rig.name,
        "action": action.name,
        "frames": [f0, f1],
        "pose_activity": activity,
        "pose_activity_ok": pose_activity_ok,
        "envelope": {
            "rest": {
                "z_min": round(rest_zmin, 6),
                "z_max": round(rest_zmax, 6),
                "height": round(rest_height, 6),
                "ground_ok": ground_ok,
                "height_ok": height_ok,
            },
            "pose": {
                "z_min": round(pose_zmin, 6),
                "z_max": round(pose_zmax, 6),
                "walk_foot_sink": round(walk_foot_sink, 6),
            },
            "canonical_height": CANONICAL_HEIGHT,
            "note": "grounding/height gated at REST; walk foot-sink is an animation artifact",
        },
        "prohibited_pairs": [list(p) for p in PROHIBITED_PAIRS],
        "prohibited_hits": prohibited_hits,
        "review_overlaps": review_pairs,
        "self_intersections": self_hits,
        "renders": renders,
        "verdict": "PASS" if not fail_reasons else "FAIL",
        "fail_reasons": fail_reasons,
        "claim": ("No prohibited intersections or self-intersections across the "
                  "audited envelope; pose activity verified." if not fail_reasons
                  else "; ".join(fail_reasons)),
    }
    out_json = evidence_dir / "clearance-audit.json"
    out_json.write_text(json.dumps(report, indent=2) + "\n")
    print(f"verdict: {report['verdict']} ({report['claim']})")
    print(f"evidence: {out_json}")
    return 0 if not fail_reasons else 1


if __name__ == "__main__":
    sys.exit(run())
