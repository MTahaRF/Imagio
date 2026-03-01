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

        with open(list_file, "w") as f:
            for vid in video_files:
                f.write(f"file '{os.path.abspath(vid)}'\n")

        cmd = f'ffmpeg -y -f concat -safe 0 -i "{list_file}" -c copy "{final_path}"'
        try:
            subprocess.run(cmd, shell=True, check=True,
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print(f"🎉 Final video: {final_path}")
            os.remove(list_file)
            return final_path
        except subprocess.CalledProcessError as e:
            print(f"❌ Merge failed: {e}")
            return None
