"""
src/tools/manim_runner.py
─────────────────────────
Executes a Manim scene file via subprocess and handles failures with a
retry loop. On every failed attempt the error log is returned so the
caller (coder agent) can attempt a fix before the next retry.

Public API
──────────
    result = render_scene(scene_file, output_dir, max_retries, on_error)
    result.success   → bool
    result.mp4_path  → str | None
    result.error_log → str | None
"""

from __future__ import annotations

import os
import subprocess
import glob
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Optional

logger = logging.getLogger(__name__)

# ── Constants ─────────────────────────────────────────────────────────────────

SCENE_CLASS   = "ImagioScene"
MANIM_QUALITY = "-qm"           # medium quality — 720p30, fast to render
DEFAULT_RETRIES = 3


# ── Result dataclass ──────────────────────────────────────────────────────────

@dataclass
class RenderResult:
    success:   bool
    mp4_path:  Optional[str] = None
    error_log: Optional[str] = None
    attempts:  int = 0
    logs:      list[str] = field(default_factory=list)

    def __str__(self) -> str:
        if self.success:
            return f"RenderResult(✅ success, mp4={self.mp4_path}, attempts={self.attempts})"
        return f"RenderResult(❌ failed after {self.attempts} attempt(s))"


# ── Core renderer ─────────────────────────────────────────────────────────────

def render_scene(
    scene_file:  str,
    output_dir:  str  = "workspace/media",
    max_retries: int  = DEFAULT_RETRIES,
    on_error:    Optional[Callable[[str, str, int], str]] = None,
) -> RenderResult:
    """
    Render `scene_file` with Manim.  Retries up to `max_retries` times.

    Parameters
    ──────────
    scene_file   : Path to the generated .py file containing ImagioScene.
    output_dir   : Root directory where Manim writes media output.
    max_retries  : Maximum number of render attempts before giving up.
    on_error     : Optional callback invoked on each failure.
                   Signature: on_error(scene_file, error_log, attempt) -> new_scene_file
                   If provided, the return value is used as the scene file for the
                   next attempt (allows the coder agent to rewrite the file in-place).

    Returns
    ───────
    RenderResult with .success, .mp4_path, .error_log, .attempts, .logs
    """
    scene_file = os.path.abspath(scene_file)
    output_dir = os.path.abspath(output_dir)
    os.makedirs(output_dir, exist_ok=True)

    result = RenderResult(success=False)

    for attempt in range(1, max_retries + 1):
        result.attempts = attempt
        logger.info(f"[manim_runner] Attempt {attempt}/{max_retries} → {scene_file}")

        attempt_result = _run_manim(scene_file, output_dir)
        result.logs.append(attempt_result["log"])

        if attempt_result["returncode"] == 0:
            # ── Success ───────────────────────────────────────────
            mp4 = _find_output_mp4(scene_file, output_dir)
            if mp4:
                result.success  = True
                result.mp4_path = mp4
                logger.info(f"[manim_runner] ✅ Rendered → {mp4}")
                return result
            else:
                error = "Manim exited 0 but no MP4 found in output directory."
                logger.warning(f"[manim_runner] {error}")
                result.error_log = error
        else:
            # ── Failure ───────────────────────────────────────────
            error_log        = attempt_result["stderr"] or attempt_result["stdout"]
            result.error_log = error_log
            logger.warning(
                f"[manim_runner] ❌ Attempt {attempt} failed.\n"
                f"  stderr: {error_log[:400]}..."
            )

            if attempt < max_retries and on_error is not None:
                logger.info("[manim_runner] Calling on_error callback for fix...")
                try:
                    fixed_file = on_error(scene_file, error_log, attempt)
                    if fixed_file and os.path.exists(fixed_file):
                        scene_file = os.path.abspath(fixed_file)
                        logger.info(f"[manim_runner] Using fixed file: {scene_file}")
                except Exception as cb_exc:
                    logger.error(f"[manim_runner] on_error callback raised: {cb_exc}")

    # ── All retries exhausted ──────────────────────────────────────────────
    logger.error(
        f"[manim_runner] All {max_retries} attempts failed for {scene_file}."
    )
    return result


# ── Subprocess helper ─────────────────────────────────────────────────────────

def _run_manim(scene_file: str, output_dir: str) -> dict:
    """Run the manim CLI and return returncode + captured output."""
    cmd = [
        "manim",
        MANIM_QUALITY,
        "--media_dir", output_dir,
        scene_file,
        SCENE_CLASS,
    ]
    logger.debug(f"[manim_runner] CMD: {' '.join(cmd)}")

    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300,          # 5-minute hard cap per render
        )
        log_line = (
            f"--- attempt stdout ---\n{proc.stdout}\n"
            f"--- attempt stderr ---\n{proc.stderr}"
        )
        return {
            "returncode": proc.returncode,
            "stdout":     proc.stdout,
            "stderr":     proc.stderr,
            "log":        log_line,
        }
    except FileNotFoundError:
        msg = (
            "Manim executable not found. "
            "Install with: pip install manim"
        )
        logger.error(f"[manim_runner] {msg}")
        return {"returncode": -1, "stdout": "", "stderr": msg, "log": msg}
    except subprocess.TimeoutExpired:
        msg = "Manim render timed out after 300 seconds."
        logger.error(f"[manim_runner] {msg}")
        return {"returncode": -1, "stdout": "", "stderr": msg, "log": msg}


# ── Output-file locator ───────────────────────────────────────────────────────

def _find_output_mp4(scene_file: str, output_dir: str) -> Optional[str]:
    """
    Manim places output at:
        <output_dir>/videos/<stem>/<quality>/<SceneName>.mp4

    We glob broadly so different quality flags still resolve.
    """
    stem = Path(scene_file).stem

    # Most specific: exact scene class name
    patterns = [
        os.path.join(output_dir, "videos", stem, "**", f"{SCENE_CLASS}.mp4"),
        os.path.join(output_dir, "videos", stem, "**", "*.mp4"),
        os.path.join(output_dir, "**", f"{SCENE_CLASS}.mp4"),
        os.path.join(output_dir, "**", "*.mp4"),
    ]

    for pattern in patterns:
        matches = glob.glob(pattern, recursive=True)
        if matches:
            # Return the most recently modified match
            return max(matches, key=os.path.getmtime)

    return None


# ── Convenience: write code string → file, then render ───────────────────────

def render_code_string(
    code:        str,
    scene_name:  str,
    code_dir:    str = "workspace/code",
    output_dir:  str = "workspace/media",
    max_retries: int = DEFAULT_RETRIES,
    on_error:    Optional[Callable[[str, str, int], str]] = None,
) -> RenderResult:
    """
    Write `code` to disk as `<code_dir>/<scene_name>.py` then render it.
    Convenience wrapper used by the pipeline for each scene.
    """
    os.makedirs(code_dir, exist_ok=True)
    scene_file = os.path.join(code_dir, f"{scene_name}.py")

    with open(scene_file, "w", encoding="utf-8") as f:
        f.write(code)

    logger.info(f"[manim_runner] Wrote scene to {scene_file}")
    return render_scene(scene_file, output_dir, max_retries, on_error)