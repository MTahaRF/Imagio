"""
test_offline.py
───────────────
Offline end-to-end test: reads a JSON fixture (no API calls), runs every scene
through its template → Manim render → FFmpeg merge into a final video.

Usage:
    python test_offline.py                       # Full render + merge
    python test_offline.py --dry-run             # Code generation only (no Manim)
    python test_offline.py --only scene_03 scene_06
    python test_offline.py --skip scene_09       # Skip picture_slide (needs Nebius)
    python test_offline.py --fixture my_data.json
    python test_offline.py --no-merge            # Render but skip merge step
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
import time
from dataclasses import dataclass
from typing import Optional

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)

from src.templates.registry import get_template
from src.tools.manim_runner import render_code_string, RenderResult
from src.tools.merger import VideoMerger

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-7s  [%(name)s]  %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)

DEFAULT_FIXTURE = os.path.join(ROOT, "test_fixtures.json")


# ── Result tracker ────────────────────────────────────────────────────────────

@dataclass
class SceneResult:
    scene_id:   str
    template:   str
    concept:    str
    success:    bool
    mp4_path:   Optional[str]
    error_log:  Optional[str]
    duration_s: float
    dry_run:    bool = False

    def status_icon(self) -> str:
        if self.dry_run:
            return "📝"
        return "✅" if self.success else "❌"


# ── Core runner ───────────────────────────────────────────────────────────────

def run_offline(
    fixture_path: str,
    only:         list[str],
    skip:         list[str],
    dry_run:      bool,
    merge:        bool,
    lang_code:    str = "en",
) -> list[SceneResult]:
    """Load the JSON fixture and run each scene through template → render."""

    # ── Load fixture ──────────────────────────────────────────────────────
    with open(fixture_path, "r", encoding="utf-8") as f:
        fixture = json.load(f)

    scenes   = fixture.get("scenes", [])
    lang     = fixture.get("language", lang_code)
    topic    = fixture.get("topic", "Unknown Topic")
    curriculum = fixture.get("curriculum", {})

    # ── Filter scenes ─────────────────────────────────────────────────────
    if only:
        scenes = [s for s in scenes if s["scene_id"] in only]
    if skip:
        scenes = [s for s in scenes if s["scene_id"] not in skip]

    total   = len(scenes)
    results: list[SceneResult] = []

    print(f"\n{'─' * 66}")
    print(f"  Imagio Offline Test Runner")
    print(f"  Topic:    {topic}")
    print(f"  Scenes:   {total}")
    print(f"  Language:  {lang}")
    if curriculum:
        print(f"  Title:    {curriculum.get('title', '')}")
    if dry_run:
        print(f"  Mode:     DRY RUN — code generation only, no Manim render")
    print(f"{'─' * 66}\n")

    # ── Per-scene loop ────────────────────────────────────────────────────
    for idx, scene in enumerate(scenes, 1):
        scene_id      = scene["scene_id"]
        template_name = scene.get("template_type", "bullet_points")
        concept       = scene.get("concept", "")
        script        = scene.get("script", "")
        template_data = scene.get("template_data", {})

        print(f"[{idx:02d}/{total:02d}]  {scene_id}  ─  {concept}  [{template_name}]")

        # ── Get template ──────────────────────────────────────────────────
        try:
            tmpl = get_template(template_name)
        except KeyError:
            print(f"        ⚠️  Unknown template '{template_name}' → bullet_points")
            tmpl = get_template("bullet_points")
            template_name = "bullet_points"

        tmpl.set_language(lang)

        # ── Generate Manim code ───────────────────────────────────────────
        t0 = time.perf_counter()
        try:
            code = tmpl.code(template_data, script)
        except Exception as exc:
            duration = time.perf_counter() - t0
            print(f"        ❌  code() raised: {exc}\n")
            results.append(SceneResult(
                scene_id=scene_id, template=template_name, concept=concept,
                success=False, mp4_path=None, error_log=str(exc),
                duration_s=duration,
            ))
            continue

        # ── Write code to disk ────────────────────────────────────────────
        code_dir = os.path.join("workspace", "code")
        os.makedirs(code_dir, exist_ok=True)
        code_path = os.path.join(code_dir, f"{scene_id}.py")
        with open(code_path, "w", encoding="utf-8") as f:
            f.write(code)

        if dry_run:
            duration = time.perf_counter() - t0
            print(f"        📝  Code written → {code_path}  ({duration:.2f}s)\n")
            results.append(SceneResult(
                scene_id=scene_id, template=template_name, concept=concept,
                success=True, mp4_path=None, error_log=None,
                duration_s=duration, dry_run=True,
            ))
            continue

        # ── Render with Manim ─────────────────────────────────────────────
        print("        ⏳  Rendering…")
        render: RenderResult = render_code_string(
            code        = code,
            scene_name  = scene_id,
            code_dir    = code_dir,
            output_dir  = "workspace/media",
            max_retries = 2,
        )
        duration = time.perf_counter() - t0

        if render.success:
            print(f"        ✅  {render.mp4_path}  ({duration:.1f}s)\n")
        else:
            short_err = (render.error_log or "")[:400].replace("\n", " ")
            print(f"        ❌  FAILED ({duration:.1f}s)")
            print(f"            {short_err}\n")

        results.append(SceneResult(
            scene_id   = scene_id,
            template   = template_name,
            concept    = concept,
            success    = render.success,
            mp4_path   = render.mp4_path,
            error_log  = render.error_log,
            duration_s = duration,
        ))

    # ── Merge ─────────────────────────────────────────────────────────────
    if merge and not dry_run:
        _merge_results(results, lang)

    return results


# ── Merge helper ──────────────────────────────────────────────────────────────

def _merge_results(results: list[SceneResult], lang: str) -> None:
    passed = [r.mp4_path for r in results if r.success and r.mp4_path]

    if not passed:
        print("\n⚠️  No videos to merge — all scenes failed.\n")
        return

    print(f"\n{'─' * 66}")
    print(f"  🎬  Merging {len(passed)} scene(s) into final video…")
    print(f"{'─' * 66}")

    merger = VideoMerger()
    final  = merger.merge_all_scenes(
        passed,
        output_filename=f"offline_test_{lang}.mp4",
    )

    if final and os.path.exists(final):
        size_mb = os.path.getsize(final) / (1024 * 1024)
        print(f"\n  ✅  Final video → {final}  ({size_mb:.1f} MB)\n")
    else:
        print("\n  ❌  Merge failed — check FFmpeg is installed and on PATH.\n")


# ── Summary ───────────────────────────────────────────────────────────────────

def print_summary(results: list[SceneResult]) -> None:
    passed = [r for r in results if r.success]
    failed = [r for r in results if not r.success]

    print(f"\n{'═' * 66}")
    print(f"  SUMMARY   {len(passed)} passed  |  {len(failed)} failed  |  {len(results)} total")
    print(f"{'═' * 66}")

    for r in results:
        icon  = r.status_icon()
        label = "DRY-RUN" if r.dry_run else ("OK" if r.success else "FAIL")
        path  = f"  →  {r.mp4_path}" if r.mp4_path else ""
        print(f"  {icon}  {r.scene_id:<12}  {r.template:<22}  {label:<8}  {r.duration_s:5.1f}s{path}")

    if failed:
        print(f"\n{'─' * 66}")
        print("  ERRORS")
        for r in failed:
            print(f"\n  ❌  {r.scene_id} [{r.template}]")
            if r.error_log:
                for line in (r.error_log[:800]).splitlines():
                    print(f"      {line}")

    print(f"\n{'═' * 66}\n")


# ── CLI ───────────────────────────────────────────────────────────────────────

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Offline end-to-end Imagio test. Reads a JSON fixture, "
            "generates Manim code, renders each scene, and merges into a final video. "
            "No API calls required."
        ),
    )
    parser.add_argument(
        "--fixture", default=DEFAULT_FIXTURE,
        help=f"Path to the JSON fixture file (default: {DEFAULT_FIXTURE})",
    )
    parser.add_argument(
        "--only", nargs="+", metavar="SCENE_ID",
        help="Only run the named scene IDs (e.g. scene_01 scene_05).",
    )
    parser.add_argument(
        "--skip", nargs="+", metavar="SCENE_ID",
        help="Skip the named scene IDs.",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Generate code files only, no Manim render.",
    )
    parser.add_argument(
        "--no-merge", action="store_true",
        help="Skip merging videos at the end.",
    )
    parser.add_argument(
        "--list", action="store_true",
        help="Print all scenes in the fixture and exit.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

    # ── List mode ─────────────────────────────────────────────────────────
    if args.list:
        with open(args.fixture, "r", encoding="utf-8") as f:
            fixture = json.load(f)
        print(f"\nFixture: {args.fixture}")
        print(f"Topic:   {fixture.get('topic', 'N/A')}\n")
        for s in fixture.get("scenes", []):
            print(f"  • {s['scene_id']:<14} [{s['template_type']:<20}]  {s.get('concept', '')}")
        print()
        sys.exit(0)

    # ── Run ───────────────────────────────────────────────────────────────
    results = run_offline(
        fixture_path = args.fixture,
        only         = args.only or [],
        skip         = args.skip or [],
        dry_run      = args.dry_run,
        merge        = not args.no_merge,
    )
    print_summary(results)
    sys.exit(1 if any(not r.success for r in results) else 0)
