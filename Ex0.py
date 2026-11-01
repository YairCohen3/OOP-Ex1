import sys
import time
from Volume import Volume
from Projector import Projector
from IO_Utils import load_planes_from_csv, save_frames_to_mp4


def main():

    if len(sys.argv) != 4:
        print("Usage: python Ex0.py data/<file.nrrd> docs/<file.csv> <file.mp4>")
        sys.exit(1)

    nrrd_path = sys.argv[1]
    csv_path = sys.argv[2]
    mp4_path = sys.argv[3]

    print(f"[1/4] Loading 3D volume from: {nrrd_path}...")
    volume = Volume(nrrd_path)
    print(f"      Volume dimensions: {volume.sx}x{volume.sy}x{volume.sz}")

    print(f"[2/4] Loading plane coordinates from: {csv_path}...")
    planes = load_planes_from_csv(csv_path)
    print(f"      Loaded {len(planes)} planes.")

    print("[3/4] Projecting planes onto 2D frames...")
    frames = []
    start_time = time.perf_counter()

    for plane in planes:
        frame = Projector.projection(volume, plane)
        frames.append(frame)

    elapsed = time.perf_counter() - start_time
    fps = len(planes) / elapsed if elapsed > 0 else float("inf")
    print(f"      Projection complete in {elapsed:.4f}s ({fps:.1f} FPS).")

    print(f"[4/4] Saving output video to: {mp4_path}...")
    save_frames_to_mp4(frames, mp4_path)
    print("Done! Video saved successfully.")


if __name__ == "__main__":
    main()