"""
sample_test.py
─────────
Test harness for all 10 Imagio templates.

Run from the project root:
    python sample_test.py
    python sample_test.py --only graph_plot equation_transform
    python sample_test.py --skip picture_slide
    python sample_test.py --dry-run
"""

from __future__ import annotations

import argparse
import logging
import os
import sys
import time
from dataclasses import dataclass
from typing import Optional

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)

from src.templates.registry import list_templates, get_template
from src.tools.manim_runner import render_code_string, RenderResult
from src.tools.merger import VideoMerger

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-7s  [%(name)s]  %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)

# ── Sample payloads ───────────────────────────────────────────────────────────

SAMPLE_DATA: dict[str, dict] = {

    "title_slide": {
        "title":     "The Fourier Transform",
        "subtitle":  "Decomposing Signals Into Frequencies",
        "narration": "Welcome to this exploration of the Fourier Transform, one of the most powerful tools in all of mathematics.",
    },

    "bullet_points": {
        "title": "Why the Fourier Transform Matters",
        "points": [
            "Converts a signal from the time domain to the frequency domain",
            "Reveals the hidden frequencies inside any waveform",
            "Powers MP3 compression, JPEG images, and noise cancellation",
            "Used in quantum mechanics and solving differential equations",
            "One of the most widely applied tools in all of mathematics",
        ],
        "narrations": [
            "The Fourier Transform moves a signal from the time domain into the frequency domain.",
            "It reveals hidden frequencies that are invisible in the original waveform.",
            "This powers everyday technology like MP3 audio and JPEG image compression.",
            "It also appears in quantum mechanics and differential equation solutions.",
            "Making it one of the most broadly applied tools across all of mathematics.",
        ],
    },

    "split_slide": {
        "title":        "The Fourier Transform Formula",
        "left_header":  "Formula",
        "left_formula": r"\hat{f}(\omega) = \int_{-\infty}^{\infty} f(t)\, e^{-i\omega t}\, dt",
        "right_header": "What it means",
        "right_lines": [
            "f(t) is the original signal in time",
            "e^(-iwt) is a rotating complex sinusoid",
            "The integral sums contributions at each frequency w",
            "The result F(w) is the amplitude at each frequency",
        ],
        "narrations": {
            "intro":   "Let us break down the Fourier Transform formula piece by piece.",
            "formula": "This integral transforms a time-domain signal into the frequency domain.",
            "lines": [
                "f of t is the original signal measured over time.",
                "The exponential term is a rotating complex sinusoid at frequency omega.",
                "The integral accumulates all contributions across every frequency.",
                "The result gives us the amplitude present at each individual frequency.",
            ],
        },
    },

    "equation_transform": {
        "title": "Deriving Euler's Identity",
        "steps": [
            r"e^{i\theta} = \cos\theta + i\sin\theta",
            r"e^{i\pi} = \cos\pi + i\sin\pi",
            r"e^{i\pi} = -1 + i \cdot 0",
            r"e^{i\pi} + 1 = 0",
        ],
        "annotations": [
            "Start with Euler's formula",
            "Substitute theta = pi",
            "Evaluate: cos(pi) = -1, sin(pi) = 0",
            "Rearrange to get the famous identity",
        ],
        "narrations": [
            "We start with Euler's formula relating the exponential to sine and cosine.",
            "Substituting theta equals pi into both sides of the equation.",
            "Evaluating cosine of pi gives negative one, and sine of pi gives zero.",
            "Rearranging gives us Euler's famous identity, considered the most beautiful equation in mathematics.",
        ],
    },

    "graph_plot": {
        "title":    "A Simple Sine Wave",
        "function": "np.sin(2 * np.pi * x)",
        "x_min":    "-2",
        "x_max":    "2",
        "y_min":    "-1.5",
        "y_max":    "1.5",
        "x_label":  "Time (s)",
        "y_label":  "Amplitude",
        "color":    "BLUE",
        "caption":  "sin(2πt) — one complete cycle per second",
        "narrations": {
            "axes":    "Let us set up the time and amplitude axes for our sine wave.",
            "graph":   "Here is the sine wave completing exactly one full cycle per second.",
            "caption": "This is sin of 2 pi t, oscillating between negative one and positive one.",
        },
    },

    "definition_slide": {
        "term":       "Eigenvalue",
        "definition": (
            "A scalar lambda is an eigenvalue of a matrix A if there exists a "
            "non-zero vector v such that Av equals lambda times v."
        ),
        "formula":    r"A\mathbf{v} = \lambda\mathbf{v}",
        "example":    "Stretching a vector without changing its direction",
        "narrations": {
            "term":       "Let us define the concept of an eigenvalue in linear algebra.",
            "definition": "An eigenvalue is a scalar that scales a vector without rotating it under a matrix transformation.",
            "formula":    "This is expressed as A times v equals lambda times v.",
            "example":    "A simple example is stretching a vector along its own direction.",
        },
    },

    "code_walkthrough": {
        "title":    "Binary Search in Python",
        "language": "Python",
        "code_lines": [
            "def binary_search(arr, target):",
            "    lo, hi = 0, len(arr) - 1",
            "    while lo <= hi:",
            "        mid = (lo + hi) // 2",
            "        if arr[mid] == target:",
            "            return mid",
            "        elif arr[mid] < target:",
            "            lo = mid + 1",
            "        else:",
            "            hi = mid - 1",
            "    return -1",
        ],
        "explanations": [
            "Define the function with a sorted list and target",
            "Initialise left and right pointers at the array bounds",
            "Loop while the search window is valid",
            "Compute the middle index",
            "Target found — return its index",
            "Target is larger — discard the left half",
            "Move lo pointer past mid",
            "Target is smaller — discard the right half",
            "Move hi pointer below mid",
            "Close the else block",
            "Target not found — return negative one",
        ],
        "narrations": [
            "We define the binary search function taking a sorted array and a target value.",
            "We initialise two pointers at the leftmost and rightmost positions.",
            "We loop as long as the search window contains at least one element.",
            "We calculate the middle index to check next.",
            "If the middle element matches the target, we return its index immediately.",
            "If the target is larger, we discard everything to the left of mid.",
            "We shift the left pointer just past mid.",
            "If the target is smaller, we discard everything to the right of mid.",
            "We shift the right pointer just below mid.",
            "This closes the else branch of our conditional check.",
            "If the loop ends without a match, we return negative one to signal not found.",
        ],
    },

    "comparison_slide": {
        "title":        "Classical vs Quantum Computing",
        "left_header":  "Classical",
        "right_header": "Quantum",
        "left_items": [
            "Uses bits: 0 or 1",
            "Sequential gate operations",
            "Deterministic output",
            "Scales polynomially",
            "Room temperature",
        ],
        "right_items": [
            "Uses qubits: superposition",
            "Parallel quantum gates",
            "Probabilistic measurement",
            "Exponential speedup",
            "Near absolute-zero cooling",
        ],
        "narrations": [
            "Classical computers use bits while quantum computers exploit superposition via qubits.",
            "Classical gates run sequentially whereas quantum gates operate in parallel.",
            "Classical results are deterministic but quantum measurement is probabilistic.",
            "Classical scaling is polynomial while quantum algorithms can offer exponential speedup.",
            "Classical machines run at room temperature but quantum hardware needs near absolute zero.",
        ],
    },

    "picture_slide": {
        "title":      "The Double Slit Experiment",
        "image_path": "",
        "caption":    "Light behaves as both a wave and a particle",
        "body_text": (
            "When electrons pass through two narrow slits, they create an "
            "interference pattern on the detector, even when fired one at a time. "
            "This demonstrates wave-particle duality."
        ),
        "narrations": {
            "image":   "Let us look at the famous double slit experiment setup.",
            "caption": "Light and matter behave simultaneously as both waves and particles.",
            "body":    "Electrons fired one at a time still produce an interference pattern, revealing their wave nature.",
        },
    },

    "blank": {
        "raw_body": "",
    },
}

# ── Sample scripts (fallback, used if template ignores script param) ──────────

SAMPLE_SCRIPTS: dict[str, str] = {
    "title_slide":       "Welcome to this exploration of the Fourier Transform.",
    "bullet_points":     "The Fourier Transform unlocks hidden frequency structure in any signal.",
    "split_slide":       "The Fourier Transform formula decomposes a signal into its frequencies.",
    "equation_transform":"Let us derive Euler's famous identity step by step.",
    "graph_plot":        "A sine wave completing one full cycle per second.",
    "definition_slide":  "An eigenvalue scales a vector without rotating it.",
    "code_walkthrough":  "Binary search halves the search space on every iteration.",
    "comparison_slide":  "Classical bits versus quantum qubits.",
    "picture_slide":     "The double slit experiment demonstrates wave-particle duality.",
    "blank":             "This is a custom animation on a blank canvas.",
}

# ── Result tracker ────────────────────────────────────────────────────────────

@dataclass
class TemplateResult:
    name:       str
    success:    bool
    mp4_path:   Optional[str]
    error_log:  Optional[str]
    duration_s: float
    dry_run:    bool = False

    def status_icon(self) -> str:
        if self.dry_run: return "📝"
        return "✅" if self.success else "❌"

# ── Main ──────────────────────────────────────────────────────────────────────

def run_tests(
    only:    list[str],
    skip:    list[str],
    dry_run: bool,
    merge:   bool,
) -> list[TemplateResult]:

    templates = list_templates()
    results: list[TemplateResult] = []

    if only:
        templates = [t for t in templates if t["name"] in only]
    if skip:
        templates = [t for t in templates if t["name"] not in skip]

    total = len(templates)
    print(f"\n{'─' * 62}")
    print(f"  Imagio Template Test Runner  ({total} templates)")
    if dry_run:
        print("  Mode: DRY RUN — code generation only, no Manim render")
    print(f"{'─' * 62}\n")

    for idx, entry in enumerate(templates, 1):
        name   = entry["name"]
        tmpl   = get_template(name)
        data   = SAMPLE_DATA.get(name, {})
        script = SAMPLE_SCRIPTS.get(name, "")

        if not data:
            logger.warning(f"No sample data for '{name}' — skipping.")
            continue

        print(f"[{idx:02d}/{total:02d}]  {name}")

        # ── Generate code ──────────────────────────────────────────────────
        t0 = time.perf_counter()
        try:
            code = tmpl.code(data, script)
        except Exception as exc:
            print(f"        ❌  code() raised: {exc}\n")
            results.append(TemplateResult(
                name=name, success=False, mp4_path=None,
                error_log=str(exc), duration_s=0.0,
            ))
            continue

        os.makedirs("workspace/code", exist_ok=True)
        scene_path = f"workspace/code/{name}.py"
        with open(scene_path, "w", encoding="utf-8") as f:
            f.write(code)

        if dry_run:
            duration = time.perf_counter() - t0
            print(f"        📝  Code written → {scene_path}  ({duration:.2f}s)\n")
            results.append(TemplateResult(
                name=name, success=True, mp4_path=None,
                error_log=None, duration_s=duration, dry_run=True,
            ))
            continue

        # ── Render ────────────────────────────────────────────────────────
        print("        ⏳  Rendering…")
        render: RenderResult = render_code_string(
            code        = code,
            scene_name  = name,
            code_dir    = "workspace/code",
            output_dir  = "workspace/media",
            max_retries = 1,
        )
        duration = time.perf_counter() - t0

        if render.success:
            print(f"        ✅  {render.mp4_path}  ({duration:.1f}s)\n")
        else:
            short_err = (render.error_log or "")[:400].replace("\n", " ")
            print(f"        ❌  FAILED ({duration:.1f}s)")
            print(f"            {short_err}\n")

        results.append(TemplateResult(
            name       = name,
            success    = render.success,
            mp4_path   = render.mp4_path,
            error_log  = render.error_log,
            duration_s = duration,
        ))

    # ── Merge all passed videos ────────────────────────────────────────────
    if merge and not dry_run:
        _merge_results(results)

    return results


def _merge_results(results: list[TemplateResult]) -> None:
    passed_videos = [r.mp4_path for r in results if r.success and r.mp4_path]

    if not passed_videos:
        print("\n⚠️  No videos to merge — all templates failed.\n")
        return

    print(f"\n{'─' * 62}")
    print(f"  🎬  Merging {len(passed_videos)} video(s) into final output…")
    print(f"{'─' * 62}")

    os.makedirs("workspace/final_vids", exist_ok=True)
    output_path = os.path.join("workspace", "final_vids", "test_final.mp4")

    merger = VideoMerger()
    final  = merger.merge_all_scenes(passed_videos, output_filename="test_final.mp4")

    if final and os.path.exists(final):
        size_mb = os.path.getsize(final) / (1024 * 1024)
        print(f"\n  ✅  Final video → {final}  ({size_mb:.1f} MB)\n")
    else:
        print("\n  ❌  Merge failed — check FFmpeg is installed and on PATH.\n")


def print_summary(results: list[TemplateResult]) -> None:
    passed = [r for r in results if r.success]
    failed = [r for r in results if not r.success]

    print(f"\n{'═' * 62}")
    print(f"  SUMMARY   {len(passed)} passed  |  {len(failed)} failed  |  {len(results)} total")
    print(f"{'═' * 62}")

    for r in results:
        icon  = r.status_icon()
        label = "DRY-RUN" if r.dry_run else ("OK" if r.success else "FAIL")
        path  = f"  →  {r.mp4_path}" if r.mp4_path else ""
        print(f"  {icon}  {r.name:<22}  {label:<8}  {r.duration_s:5.1f}s{path}")

    if failed:
        print(f"\n{'─' * 62}")
        print("  ERRORS")
        for r in failed:
            print(f"\n  ❌  {r.name}")
            if r.error_log:
                for line in (r.error_log[:800]).splitlines():
                    print(f"      {line}")

    print(f"\n{'═' * 62}\n")

# ── CLI ───────────────────────────────────────────────────────────────────────

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run Imagio template tests via registry + manim_runner."
    )
    parser.add_argument(
        "--only", nargs="+", metavar="TEMPLATE",
        help="Only test the named templates (space-separated).",
    )
    parser.add_argument(
        "--skip", nargs="+", metavar="TEMPLATE",
        help="Skip the named templates.",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Generate code files only, no Manim render.",
    )
    parser.add_argument(
        "--no-merge", action="store_true",
        help="Skip merging videos at the end (merge is ON by default).",
    )
    parser.add_argument(
        "--list", action="store_true",
        help="Print all registered template names and exit.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

    if args.list:
        print("\nRegistered templates:")
        for t in list_templates():
            print(f"  • {t['name']}")
            print(f"    {t['description'][:90]}...")
        print()
        sys.exit(0)

    results = run_tests(
        only    = args.only or [],
        skip    = args.skip or [],
        dry_run = args.dry_run,
        merge   = not args.no_merge,
    )
    print_summary(results)
    sys.exit(1 if any(not r.success for r in results) else 0)
