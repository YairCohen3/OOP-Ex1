import os
import subprocess
import sys
import time
from Volume import Volume
from Projector import Projector
from IO_Utils import load_planes_from_csv, save_frames_to_mp4


def open_and_play_video(video_path: str):
    """פותח את הסרטון בנגן המדיה המוגדר במחשב (מנוטרל בזמן טסטים)."""
    # אם הטסטים של pytest רצים ברקע, לא נקפיץ נגן מדיה
    if "PYTEST_CURRENT_TEST" in os.environ:
        return

    abs_path = os.path.abspath(video_path)
    try:
        if sys.platform.startswith("win"):
            os.startfile(abs_path)
        elif sys.platform.startswith("darwin"):
            subprocess.Popen(["open", abs_path])
        else:
            subprocess.Popen(["xdg-open", abs_path])
    except Exception as err:
        print(f"Note: Could not automatically open video player: {err}")


def main():

    if len(sys.argv) != 4:
        print("Usage: python Ex0.py data/<file.nrrd> docs/<file.csv> results/<file.mp4>")
        sys.exit(1)

    nrrd_path = sys.argv[1]
    csv_path = sys.argv[2]
    mp4_path = sys.argv[3]

    print(f"[1/4] Loading 3D volume from: {nrrd_path}...")
    volume = Volume(nrrd_path)
    print(f"      Volume dimensions: {volume.sx}x{volume.sy}x{volume.sz}")

    print(f"[2/4] Loading plane coordinates from: {csv_path}...")
    planes = load_planes_from_csv(csv_path, ignore_errors=True)
    print(f"      Loaded {len(planes)} planes.")

    print("[3/4] Projecting planes onto 2D frames...")
    start_time = time.perf_counter()

    frames = [Projector.projection(volume, plane) for plane in planes]

    elapsed = time.perf_counter() - start_time
    fps = len(planes) / elapsed if elapsed > 0 else float("inf")
    print(f"      Projection complete in {elapsed:.4f}s ({fps:.1f} FPS).")

    print(f"[4/4] Saving output video to: {mp4_path}...")
    save_frames_to_mp4(frames, mp4_path)
    print("Done! Video saved successfully.")

    # פתיחה וניגון אוטומטי של הסרטון
    print(f"Playing video: {mp4_path}...")
    open_and_play_video(mp4_path)


if __name__ == "__main__":
    main()