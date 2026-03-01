"""
test_pipeline.py
────────────────
End-to-end pipeline test for Imagio.
Runs the full pipeline with a simple topic and prints live status.

Usage:
    python test_pipeline.py
    python test_pipeline.py --topic "How does gravity work"
    python test_pipeline.py --dry-run       # LLM calls only, no Manim render
    python test_pipeline.py --no-merge      # render scenes but skip final concat
"""

from __future__ import annotations

import argparse
import os
import sys
import time
import traceback

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)

# ── Core ──────────────────────────────────────────────────────────────────────
from src.config import Config
from src.llm_client import ClientFactory

# ── Agents ────────────────────────────────────────────────────────────────────
from src.agents.feasibility    import FeasibilityAgent
from src.agents.planner        import ScenePlanner
from src.agents.scene_director import SceneDirector

# ── Tools ─────────────────────────────────────────────────────────────────────
from src.tools.manim_runner import render_code_string
from src.tools.merger       import VideoMerger
from src.templates.registry import get_template


# ── Pretty printers ───────────────────────────────────────────────────────────
def divider(label: str = ""):
    width = 62
    if label:
        pad = (width - len(label) - 2) // 2
        print(f"\n{'─' * pad} {label} {'─' * pad}")
    else:
        print("─" * width)

def ok(msg):   print(f"  ✅ {msg}")
def err(msg):  print(f"  ❌ {msg}")
def info(msg): print(f"  ℹ️  {msg}")
def warn(msg): print(f"  ⚠️  {msg}")


# ── Main test ─────────────────────────────────────────────────────────────────
def run_test(topic: str, dry_run: bool, no_merge: bool):

    print(f"\n{'═' * 62}")
    print(f"  🎬  IMAGIO PIPELINE TEST")
    print(f"  Topic    : {topic}")
    print(f"  Dry Run  : {dry_run}")
    print(f"  Merge    : {'disabled' if no_merge else 'enabled'}")
    print(f"{'═' * 62}")

    total_start = time.perf_counter()

    # ── Step 1: Initialise agents ─────────────────────────────────
    divider("STEP 1: Initialising Agents")
    try:
        feasibility_agent = FeasibilityAgent(ClientFactory.get_client(Config.FEASIBILITY_CONFIG))
        planner_agent     = ScenePlanner(ClientFactory.get_client(Config.PLANNER_CONFIG))
        director_agent    = SceneDirector(ClientFactory.get_client(Config.DIRECTOR_CONFIG))
        merger_tool       = VideoMerger()
        ok("All agents initialised")
        info(f"Feasibility : {Config.FEASIBILITY_CONFIG['model']}")
        info(f"Planner     : {Config.PLANNER_CONFIG['model']}")
        info(f"Director    : {Config.DIRECTOR_CONFIG['model']}")
    except Exception as e:
        err(f"Initialisation failed: {e}")
        traceback.print_exc()
        return

    # ── Step 2: Feasibility ───────────────────────────────────────
    divider("STEP 2: Feasibility + Curriculum")
    t0 = time.perf_counter()
    try:
        analysis = feasibility_agent.analyze_topic(topic)
        print(f"  Feasible : {analysis.get('feasible')}")
        print(f"  Reason   : {analysis.get('reason', 'N/A')}")
    except Exception as e:
        err(f"Feasibility check crashed: {e}")
        traceback.print_exc()
        return

    if not analysis.get("feasible"):
        err(f"Topic rejected → {analysis.get('reason')}")
        return

    curriculum = analysis.get("curriculum")
    if not curriculum:
        err("No curriculum returned — check FEASIBILITY_ENHANCER prompt")
        return

    ok(f"Approved: \"{curriculum.get('title', topic)}\"")
    ok(f"Teaching angle: {curriculum.get('teaching_angle', 'N/A')}")
    print(f"  ⏱️  {time.perf_counter() - t0:.1f}s")

    # ── Step 3: Scene planning ────────────────────────────────────
    divider("STEP 3: Scene Planning")
    t0 = time.perf_counter()
    try:
        scene_plans = planner_agent.plan_scenes(curriculum)
    except Exception as e:
        err(f"Planner crashed: {e}")
        traceback.print_exc()
        return

    if not scene_plans:
        err("Planner returned an empty scene list")
        return

    ok(f"{len(scene_plans)} scenes planned:")
    for i, plan in enumerate(scene_plans, 1):
        template = plan.get("template_type") or plan.get("template", "?")
        concept  = plan.get("concept", "?")
        print(f"    Scene {i:02d}: [{template:<22}] {concept}")
    print(f"  ⏱️  {time.perf_counter() - t0:.1f}s")

    if dry_run:
        info("Dry run — stopping before production")
        total = time.perf_counter() - total_start
        print(f"\n{'═' * 62}")
        print(f"  ✨ DRY RUN DONE in {total:.1f}s")
        print(f"{'═' * 62}\n")
        return

    # ── Step 4: Production loop ───────────────────────────────────
    divider("STEP 4: Production Loop")

    final_videos   = []
    prev_script    = ""
    scene_count    = len(scene_plans)

    for i, plan in enumerate(scene_plans, 1):
        scene_id      = f"scene_{i:02d}"
        template_name = plan.get("template_type") or plan.get("template", "bullet_points")
        concept       = plan.get("concept", "Untitled")

        print(f"\n  ┌─ Scene {i}/{scene_count}: {concept}")
        print(f"  │  Template : {template_name}")

        # ── 4A: Resolve template ──────────────────────────────────
        try:
            tmpl = get_template(template_name)
        except KeyError:
            warn(f"Unknown template '{template_name}' → falling back to bullet_points")
            tmpl          = get_template("bullet_points")
            template_name = "bullet_points"

        # ── 4B: SceneDirector — script + template_data in one shot ─
        print(f"  │  ✍️  Directing scene...")
        t0 = time.perf_counter()
        try:
            direction = director_agent.direct_scene(
                template_name   = template_name,
                schema          = tmpl.schema(),
                concept         = concept,
                previous_script = prev_script,
            )
        except Exception as e:
            err(f"SceneDirector crashed: {e}")
            traceback.print_exc()
            continue

        script        = direction.get("script", concept)
        template_data = direction.get("template_data", {})
        prev_script   = script

        if not template_data:
            warn("Director returned empty template_data — scene may look sparse")

        script_preview = script[:80].replace("\n", " ").strip()
        print(f"  │  Script   : {script_preview}...")
        print(f"  │  ⏱️  {time.perf_counter() - t0:.1f}s")

        # ── 4C: Generate Manim code ───────────────────────────────
        print(f"  │  👨‍💻 Generating Manim code...")
        t0 = time.perf_counter()
        try:
            scene_code = tmpl.code(template_data, script)
        except Exception as e:
            err(f"tmpl.code() crashed: {e}")
            traceback.print_exc()
            continue

        os.makedirs("workspace/code", exist_ok=True)
        code_path = f"workspace/code/{scene_id}.py"
        with open(code_path, "w", encoding="utf-8") as f:
            f.write(scene_code)
        print(f"  │  Code     : {code_path}  ({len(scene_code)} chars)  ⏱️  {time.perf_counter() - t0:.1f}s")

        # ── 4D: Render ────────────────────────────────────────────
        print(f"  │  🎥 Rendering...")
        t0 = time.perf_counter()
        try:
            result = render_code_string(
                code       = scene_code,
                scene_name = scene_id,
                code_dir   = "workspace/code",
                output_dir = "workspace/media",
                max_retries = 3,
            )
        except Exception as e:
            err(f"Renderer crashed: {e}")
            traceback.print_exc()
            continue

        elapsed = time.perf_counter() - t0

        if not result.success:
            err(f"Render failed after {result.attempts} attempt(s)  ⏱️  {elapsed:.1f}s")
            if result.error_log:
                snippet = result.error_log.strip()[-400:].replace("\n", " ")
                print(f"  │  Last error: {snippet}")
            print(f"  └─ skipping scene")
            continue

        print(f"  │  ✅ {result.mp4_path}  ⏱️  {elapsed:.1f}s")
        print(f"  └─ done")
        final_videos.append(result.mp4_path)

    # ── Step 5: Final assembly ────────────────────────────────────
    divider("STEP 5: Final Assembly")

    if not final_videos:
        err("No scenes rendered — pipeline failed entirely")
        total = time.perf_counter() - total_start
        print(f"\n{'═' * 62}")
        print(f"  ⏱️  Total time: {total:.1f}s")
        print(f"{'═' * 62}\n")
        return

    ok(f"{len(final_videos)}/{scene_count} scenes rendered successfully")

    if no_merge:
        info("Merge skipped (--no-merge). Individual videos:")
        for v in final_videos:
            print(f"    → {v}")
    elif len(final_videos) == 1:
        ok(f"Single scene — no merge needed → {final_videos[0]}")
    else:
        print(f"  🎞️  Merging {len(final_videos)} scenes...")
        try:
            final_path = merger_tool.merge_all_scenes(
                final_videos,
                output_filename="pipeline_final.mp4",
            )
            if final_path and os.path.exists(final_path):
                size_mb = os.path.getsize(final_path) / (1024 * 1024)
                ok(f"Final video → {final_path}  ({size_mb:.1f} MB)")
            else:
                err("Merge returned no output — check FFmpeg is on PATH")
                info("Individual scene videos:")
                for v in final_videos:
                    print(f"    → {v}")
        except Exception as e:
            err(f"Final merge crashed: {e}")
            traceback.print_exc()

    total = time.perf_counter() - total_start
    print(f"\n{'═' * 62}")
    print(f"  ✨ DONE in {total:.1f}s")
    print(f"{'═' * 62}\n")


# ── CLI ───────────────────────────────────────────────────────────────────────
def parse_args():
    parser = argparse.ArgumentParser(description="Imagio end-to-end pipeline test")
    parser.add_argument(
        "--topic", type=str,
        default="How does the Pythagorean theorem work",
        help="Educational topic to generate a video for",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Run LLM steps only — skip Manim rendering",
    )
    parser.add_argument(
        "--no-merge", action="store_true",
        help="Render scenes but skip final video concatenation",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    run_test(
        topic    = args.topic,
        dry_run  = args.dry_run,
        no_merge = args.no_merge,
    )
