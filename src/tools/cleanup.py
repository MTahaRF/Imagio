# src/tools/cleanup.py
"""
Post-pipeline cleanup utility.
Removes all intermediate files produced during a run,
keeping only the final merged video.
"""

import os
import shutil
from pathlib import Path


def cleanup(
    workspace_dir:    str  = "workspace",
    remove_code:      bool = True,   # generated .py scene files
    remove_partials:  bool = True,   # Manim partial_movie_files
    remove_scenes:    bool = True,   # individual rendered scene .mp4s
    remove_tts_cache: bool = True,   # Piper .mp3 cache in temp
    verbose:          bool = True,
) -> dict[str, int]:
    """
    Clean up after a pipeline run.
    Returns a dict of { category: files_removed }.
    """

    removed = {
        "code":      0,
        "partials":  0,
        "scenes":    0,
        "tts_cache": 0,
    }

    def _log(msg: str):
        if verbose:
            print(f"  🧹 {msg}")

    ws = Path(workspace_dir)

    # ── 1. Generated scene code ───────────────────────────────────
    if remove_code:
        code_dir = ws / "code"
        if code_dir.exists():
            files = list(code_dir.glob("scene_*.py"))
            for f in files:
                f.unlink()
                removed["code"] += 1
            _log(f"Removed {removed['code']} generated scene .py files")

    # ── 2. Manim partial movie files ──────────────────────────────
    if remove_partials:
        media_dir = ws / "media"
        for partial_dir in media_dir.rglob("partial_movie_files"):
            if partial_dir.is_dir():
                count = len(list(partial_dir.glob("*.mp4")))
                shutil.rmtree(partial_dir, ignore_errors=True)
                removed["partials"] += count
        _log(f"Removed {removed['partials']} Manim partial movie files")

    # ── 3. Individual rendered scene .mp4s ────────────────────────
    if remove_scenes:
        media_dir = ws / "media"
        # Manim writes to: media/videos/<scene_name>/<quality>/ImagioScene.mp4
        for mp4 in media_dir.rglob("ImagioScene.mp4"):
            mp4.unlink()
            removed["scenes"] += 1
        # Also clean up the empty scene subdirectories
        videos_dir = media_dir / "videos"
        if videos_dir.exists():
            for scene_dir in videos_dir.iterdir():
                if scene_dir.is_dir():
                    try:
                        # Only remove if empty after cleanup
                        if not any(scene_dir.rglob("*")):
                            shutil.rmtree(scene_dir, ignore_errors=True)
                    except Exception:
                        pass
        _log(f"Removed {removed['scenes']} individual scene .mp4 files")

    # ── 4. Piper TTS .mp3 cache ───────────────────────────────────
    if remove_tts_cache:
        import tempfile
        tts_cache = Path(tempfile.gettempdir()) / "piper_cache"
        if tts_cache.exists():
            files = list(tts_cache.glob("*.mp3")) + list(tts_cache.glob("*.wav"))
            for f in files:
                f.unlink()
                removed["tts_cache"] += 1
        # Also clean Manim-Voiceover's own cache dir (sits next to media/)
        mv_cache = ws / "media" / "voiceovers"
        if mv_cache.exists():
            for f in mv_cache.rglob("*.mp3"):
                f.unlink()
                removed["tts_cache"] += 1
        _log(f"Removed {removed['tts_cache']} TTS cache files")

    total = sum(removed.values())
    if verbose:
        print(f"  ✅ Cleanup done — {total} files removed")

    return removed
