# Changelog

All notable changes to the Imagio project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [Unreleased] - 2026-09-06

### Added
- **Live Subtitle Captions Footer**: Integrated an automated, responsive subtitle card into `ImagioScene.voiceover()` in `src/templates/base.py`. Displays narration text centered at the bottom of the screen inside a translucent rounded container (`#030712`, 85% opacity, `#3b82f6` border) with automatic text wrapping.
- **LaTeX Compatibility Wrapper for `MathTex`**: Added a fallback wrapper in `src/templates/base.py` that intercepts LaTeX compilation failures (e.g., when `latex.exe` / `dvisvgm` are not installed) and seamlessly renders clean unicode mathematical `Text` VMobjects (`∫`, `∞`, `ω`, `π`, `σ`, `θ`, `α`, `√`, `∑`, `·`, etc.), preserving all animations (`Write`, `TransformMatchingShapes`, `_safe_fit`).
- **Active Item Highlighting & Dimming**: In `bullet_points.py` and `split_slide.py`, previously spoken bullet rows are dimmed to 45% opacity while the active row remains at 100% opacity, synchronizing the viewer's focus with the narration.
- **Dynamic Animation Pacing (`tracker.duration`)**: Scaled animation durations to voiceover audio length in `bullet_points.py`, `graph_plot.py`, `split_slide.py`, and `title_slide.py` to eliminate dead static pauses.
- **Audio Padding & Drift Prevention**: Updated `VideoMerger` in `src/tools/merger.py` to pad each scene's audio stream with silence (`-af "apad" -c:v copy -c:a aac -shortest`) prior to concatenation, ensuring audio and video durations match to the exact millisecond across all scenes.
- **Offline Test Suite**: Added `test_fixtures.json` (10-scene curriculum covering all template types) and `test_offline.py` runner supporting `--only`, `--skip`, `--dry-run`, `--list`, and `--no-merge` flags.
- **Text Outflow Prevention**: Introduced `_safe_fit()`, `_wrap_text()`, and dynamic font sizing helpers across all 10 templates, paired with prompt constraints in `src/prompts.py` enforcing concise on-screen copy.

### Fixed
- **Scene Render Crashes**: Resolved `FileNotFoundError: [WinError 2]` in `definition_slide`, `split_slide`, and `equation_transform` when rendering on systems without a local LaTeX distribution.
- **Audio-Video Desynchronization**: Resolved a cumulative drift where audio was jumping ahead by ~3.5 seconds at every scene transition during concatenation.
- **Subtitle Text Truncation**: Fixed premature mid-sentence text splitting on the title screen by preserving full narration beats up to 140 characters in a single card.
- **Virtualenv Manim Execution**: Updated `src/tools/manim_runner.py` to invoke `[sys.executable, "-m", "manim"]` rather than relying on system `PATH`.
- **Horizontal & Vertical Text Outflow**: Prevented text clipping and off-screen overflow across all 10 slide templates.

### Changed
- **Watermark Positioning**: Relocated the "Made by Imagio" footer watermark to the bottom-right corner (`buff=0.18`, font size 11, muted slate `#475569`) to prevent overlap with centered subtitles.
- **Scene Pacing**: Shortened scene end pauses from 2.0s to 1.0s and entry/exit buffers from 0.5s to 0.25s for tighter, more dynamic video flow.
