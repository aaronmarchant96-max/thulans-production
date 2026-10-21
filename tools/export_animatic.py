#!/usr/bin/env python3
"""
Thulan Motion Comic Animatic Compiler (24fps Master)
Authority: SHOT_LEDGER.csv, Take 7 Audio Master
Owner: Aaron Marchant
"""

import sys
import os
import csv
import json
import subprocess
import argparse
from pathlib import Path

DEFAULT_PRODUCTION_ROOT = Path("/home/aaron/animation/thulans-production")
DEFAULT_LEDGER = DEFAULT_PRODUCTION_ROOT / "episodes/001_eleven_bells/SHOT_LEDGER.csv"
DEFAULT_STORYBOARD = DEFAULT_PRODUCTION_ROOT / "episodes/001_eleven_bells/storyboard"
DEFAULT_OUTPUT = DEFAULT_PRODUCTION_ROOT / "episodes/001_eleven_bells/eleven_bells_animatic.mp4"

# Fallback audio candidates in order of preference
AUDIO_CANDIDATES = [
    Path("/home/aaron/Downloads/THULANS_Eleven_Bells_Cinematic_3m30_Master.wav"),
    Path("/home/aaron/Downloads/THULANS_Eleven_Bells_Clean_Uncut_Master.wav"),
    DEFAULT_PRODUCTION_ROOT / "episodes/001_eleven_bells/assets/user_instrumental_take2_mastered_48k24.wav"
]

# Bell strike cue timestamps (seconds from start of master timeline)
BELL_CUES = {
    "bell_1": 71.28,
    "bell_3": 84.66,
    "bell_5": 104.58,
    "bell_7": 127.66,
    "door_slam": 156.32,
    "bell_11": 161.82
}

def parse_timecode(tc_str):
    """Converts MM:SS.SS to total float seconds."""
    parts = tc_str.strip().split(":")
    if len(parts) == 2:
        return float(parts[0]) * 60.0 + float(parts[1])
    return float(tc_str)

def get_audio_duration(audio_path):
    cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        str(audio_path)
    ]
    res = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return float(res.stdout.strip())

def resolve_plate_for_shot(shot_id, storyboard_dir):
    """Maps a shot ID to the best available storyboard plate."""
    shot_map = {
        "SHOT_01": "panel_01_the_throat.jpg",
        "SHOT_02": "panel_02.jpg",
        "SHOT_03": "plate_03_the_breaker_cadence_canon.jpg",
        "SHOT_04": "plate_02_the_welded_profile_canon.jpg",
        "SHOT_05": "panel_04_the_iron_bell.jpg",
        "SHOT_06": "panel_05_pressure_rupture.jpg",
        "SHOT_07": "panel_06_cable_snap.jpg",
        "SHOT_08": "panel_07_locked_harnesses.jpg",
        "SHOT_09": "panel_07_locked_harnesses.jpg",
        "SHOT_10": "panel_03_the_welded_canon.jpg",
        "SHOT_11": "panel_08_jammed_hoist.jpg",
        "SHOT_12": "panel_09_eleventh_bell.jpg",
        "SHOT_13": "panel_10_council_plaque.jpg",
        "SHOT_14": "plate_01_thulan_mastercraft_canon.jpg",
    }
    target = shot_map.get(shot_id, "panel_01_the_throat.jpg")
    p = storyboard_dir / target
    if p.exists():
        return p

    # Fallbacks if plate is not yet generated
    fallbacks = [
        storyboard_dir / "panel_01_the_throat.jpg",
        storyboard_dir / "plate_02_the_welded_profile_canon.jpg",
        storyboard_dir / "plate_03_the_breaker_cadence_canon.jpg",
    ]
    for fb in fallbacks:
        if fb.exists():
            return fb
    return None

def build_animatic_plan(ledger_path, audio_path, storyboard_dir):
    shots = []
    with open(ledger_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            start_s = parse_timecode(row["TC_Start"])
            end_s = parse_timecode(row["TC_End"])
            duration_s = end_s - start_s
            plate_path = resolve_plate_for_shot(row["Shot_ID"], storyboard_dir)
            shots.append({
                "shot_id": row["Shot_ID"],
                "start": start_s,
                "end": end_s,
                "duration": duration_s,
                "phrase": row["Narration_Phrase"],
                "subject": row["Visual_Subject"],
                "motion": row["Motion_Type"],
                "plate": plate_path
            })

    audio_dur = get_audio_duration(audio_path)
    return shots, audio_dur

def main():
    parser = argparse.ArgumentParser(description="Compile Thulan Motion Comic Animatic")
    parser.add_argument("--ledger", type=Path, default=DEFAULT_LEDGER)
    parser.add_argument("--audio", type=Path, default=None)
    parser.add_argument("--storyboard", type=Path, default=DEFAULT_STORYBOARD)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--fps", type=int, default=24)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    # Resolve audio path
    audio_path = args.audio
    if not audio_path or not audio_path.exists():
        for candidate in AUDIO_CANDIDATES:
            if candidate.exists():
                audio_path = candidate
                break
    if not audio_path or not audio_path.exists():
        print(f"Error: No valid audio master found. Provide --audio.", file=sys.stderr)
        sys.exit(1)

    print(f"==================================================")
    print(f"  THULAN MOTION COMIC ANIMATIC COMPILER (24 FPS)")
    print(f"  Audio Master: {audio_path.name}")
    print(f"  Ledger: {args.ledger}")
    print(f"==================================================")

    shots, audio_dur = build_animatic_plan(args.ledger, audio_path, args.storyboard)
    print(f"Loaded {len(shots)} shots. Audio Duration: {audio_dur:.2f}s")

    if args.dry_run:
        print("\n--- TIMELINE DRY-RUN VERIFICATION ---")
        for s in shots:
            plate_name = s["plate"].name if s["plate"] else "MISSING"
            print(f"[{s['shot_id']}] {s['start']:06.2f}s -> {s['end']:06.2f}s (dur: {s['duration']:05.2f}s) | Plate: {plate_name}")
            print(f"       Action: {s['phrase'][:60]}...")
        print(f"\nTotal Shots Span: {shots[-1]['end']:.2f}s | Audio: {audio_dur:.2f}s")
        diff = abs(shots[-1]["end"] - audio_dur)
        print(f"Sync Variance: {diff:.3f}s")
        return

    # Render segments
    tmp_dir = args.output.parent / "tmp_animatic"
    tmp_dir.mkdir(parents=True, exist_ok=True)
    concat_list = tmp_dir / "concat_list.txt"

    segment_files = []
    with open(concat_list, "w") as cl:
        for idx, s in enumerate(shots):
            seg_out = tmp_dir / f"seg_{idx:02d}_{s['shot_id']}.mp4"
            segment_files.append(seg_out)
            cl.write(f"file '{seg_out.resolve()}'\n")

            if seg_out.exists() and seg_out.stat().st_size > 1000:
                print(f"[{idx+1}/{len(shots)}] Reusing {seg_out.name} ({s['duration']:.2f}s)")
                continue

            print(f"[{idx+1}/{len(shots)}] Rendering {s['shot_id']} ({s['duration']:.2f}s) -> {seg_out.name}")
            # Calculate shake offset if bell strikes or door slam occurs in this shot
            shake_x_terms = []
            shake_y_terms = []
            for bname, btime in BELL_CUES.items():
                if s["start"] <= btime <= s["end"]:
                    rel_t = btime - s["start"]
                    print(f"       -> [AUDIO CUE] {bname} at timeline {btime:.2f}s (shot rel: {rel_t:.2f}s)")
                    shake_x_terms.append(f"(between(t,{rel_t:.2f},{rel_t+0.4:.2f})*sin(2*PI*15*(t-{rel_t:.2f}))*exp(-6*(t-{rel_t:.2f}))*18)")
                    shake_y_terms.append(f"(between(t,{rel_t:.2f},{rel_t+0.4:.2f})*cos(2*PI*15*(t-{rel_t:.2f}))*exp(-6*(t-{rel_t:.2f}))*14)")

            shake_x_expr = " + ".join(shake_x_terms) if shake_x_terms else "0"
            shake_y_expr = " + ".join(shake_y_terms) if shake_y_terms else "0"

            num_frames = max(int(round(s["duration"] * args.fps)), 1)
            
            # Smooth diagonal pan + clamped impulse shake on cue strikes
            x_expr = f"clip((in_w-out_w)/2 + ((in_w-out_w)/4)*(n/{num_frames}) + {shake_x_expr}, 0, in_w-out_w)"
            y_expr = f"clip((in_h-out_h)/2 + ((in_h-out_h)/4)*(n/{num_frames}) + {shake_y_expr}, 0, in_h-out_h)"

            vf = (
                f"scale=2048:1152,"
                f"crop=1920:1080:'{x_expr}':'{y_expr}',"
                f"format=yuv420p"
            )

            cmd = [
                "ffmpeg", "-y",
                "-loop", "1",
                "-i", str(s["plate"]),
                "-vf", vf,
                "-t", f"{s['duration']:.3f}",
                "-r", str(args.fps),
                "-c:v", "libx264",
                "-preset", "fast",
                "-crf", "18",
                "-pix_fmt", "yuv420p",
                "-an",
                str(seg_out)
            ]
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, check=True)

    # Concat and multiplex with master audio
    print("\nConcatenating shot segments and multiplexing master audio...")
    cmd_mux = [
        "ffmpeg", "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", str(concat_list),
        "-i", str(audio_path),
        "-c:v", "copy",
        "-c:a", "aac",
        "-b:a", "320k",
        "-shortest",
        str(args.output)
    ]
    subprocess.run(cmd_mux, check=True)
    print(f"\n✓ ANIMATIC MASTER READY: {args.output} ({args.output.stat().st_size} bytes)")

if __name__ == "__main__":
    main()
