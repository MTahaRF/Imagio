# src/tools/merger.py
import os
import subprocess
from ..config import Config

class VideoMerger:
    def __init__(self):
        self.final_dir = os.path.join(Config.OUTPUT_DIR, "final")
        os.makedirs(self.final_dir, exist_ok=True)

    def merge_all_scenes(self, video_files: list, output_filename: str = "final_video.mp4") -> str:
        """Concatenates a list of MP4 files into one final video."""
        if not video_files:
            return None

        print(f"\n🎬 Concatenating {len(video_files)} scenes...")

        list_file = os.path.join(Config.OUTPUT_DIR, "concat_list.txt")
        final_path = os.path.join(self.final_dir, output_filename)

        # Pad each scene's audio stream to match its video duration.
        # This prevents cumulative audio-video drift across scene cuts.
        padded_files = []
        for vid in video_files:
            abs_vid = os.path.abspath(vid)
            padded_vid = abs_vid.replace(".mp4", "_padded.mp4")
            cmd_pad = f'ffmpeg -y -i "{abs_vid}" -af "apad" -c:v copy -c:a aac -shortest "{padded_vid}"'
            try:
                subprocess.run(
                    cmd_pad, shell=True, check=True,
                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                )
                padded_files.append(padded_vid)
            except Exception:
                padded_files.append(abs_vid)

        with open(list_file, "w") as f:
            for vid in padded_files:
                f.write(f"file '{vid}'\n")

        cmd = f'ffmpeg -y -f concat -safe 0 -i "{list_file}" -c copy "{final_path}"'
        try:
            subprocess.run(
                cmd, shell=True, check=True,
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            )
            print(f"🎉 Final video: {final_path}")
            if os.path.exists(list_file):
                os.remove(list_file)
            for p in padded_files:
                if p.endswith("_padded.mp4") and os.path.exists(p):
                    try:
                        os.remove(p)
                    except OSError:
                        pass
            return final_path
        except subprocess.CalledProcessError as e:
            print(f"❌ Merge failed: {e}")
            return None
