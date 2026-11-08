# src/tools/merger.py
import os
import subprocess
from pathlib import Path

import imageio_ffmpeg

from ..config import Config

class VideoMerger:
    def __init__(self):
        self.final_dir = os.path.join(Config.OUTPUT_DIR, "final")
        os.makedirs(self.final_dir, exist_ok=True)

    def merge_all_scenes(
        self, video_files: list, output_filename: str = "final_video.mp4"
    ) -> str | None:
        """Concatenates a list of MP4 files into one final video."""
        if not video_files:
            return None

        print(f"\n🎬 Concatenating {len(video_files)} scenes...")

        list_file = Path(Config.OUTPUT_DIR) / "concat_list.txt"
        final_path = Path(self.final_dir) / output_filename
        ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()

        # Pad each scene's audio stream to match its video duration.
        # This prevents cumulative audio-video drift across scene cuts.
        padded_files = []
        for vid in video_files:
            abs_vid = Path(vid).resolve()
            padded_vid = abs_vid.with_name(f"{abs_vid.stem}_padded{abs_vid.suffix}")
            try:
                subprocess.run(
                    [
                        ffmpeg, "-y", "-i", str(abs_vid), "-af", "apad",
                        "-c:v", "copy", "-c:a", "aac", "-shortest", str(padded_vid),
                    ],
                    check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE,
                    text=True,
                )
                padded_files.append(str(padded_vid))
            except subprocess.CalledProcessError as exc:
                print(f"⚠️  Could not pad audio for {abs_vid}; using original clip.")
                if exc.stderr:
                    print(exc.stderr.strip())
                padded_files.append(str(abs_vid))

        with list_file.open("w", encoding="utf-8") as f:
            for vid in padded_files:
                f.write(f"file '{Path(vid).as_posix()}'\n")

        try:
            subprocess.run(
                [
                    ffmpeg, "-y", "-f", "concat", "-safe", "0",
                    "-i", str(list_file), "-c", "copy", str(final_path)
                ],
                check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE,
                text=True,
            )
            print(f"🎉 Final video: {final_path}")
            list_file.unlink(missing_ok=True)
            for p in padded_files:
                padded_path = Path(p)
                if padded_path.name.endswith("_padded.mp4") and padded_path.exists():
                    padded_path.unlink()
            return str(final_path)
        except subprocess.CalledProcessError as exc:
            print(f"❌ FFmpeg concatenation failed with exit code {exc.returncode}.")
            if exc.stderr:
                print(exc.stderr.strip())
            return None
