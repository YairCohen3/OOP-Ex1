import re
from typing import List
import numpy as np
import cv2
from plane import Plane


def load_planes_from_csv(csv_path: str):

    planes = []

    number_pattern = re.compile(r"[-+]?\d*\.?\d+")

    with open(csv_path, mode="r", encoding="utf-8") as f:
        for row_idx, line in enumerate(f):
            stripped = line.strip()

            if not stripped or stripped.startswith("#"):
                continue

            letters = re.findall(r"[a-zA-Z]+", stripped)
            if letters:
                continue

            values = [float(x) for x in number_pattern.findall(stripped)]
            if not values:
                continue

            if len(values) in (10, 13):
                values = values[1:]

            if len(values) == 9:
                points = np.array(values, dtype=np.float64).reshape((3, 3))
            elif len(values) == 12:
                points = np.array(values, dtype=np.float64).reshape((4, 3))
            else:
                raise ValueError(
                    f"Row {row_idx + 1} has {len(values)} numbers. "
                    f"Expected 9 (3 points) or 12 (4 points)."
                )

            planes.append(Plane(points))

    return planes


def save_frames_to_mp4(frames: List[np.ndarray], output_path: str, fps: int = 30):

    if not frames:
        raise ValueError("Cannot create MP4 video from an empty list of frames.")

    # מציאת הגובה והרוחב המקסימליים כדי שכל הפריימים בסרטון יהיו בגודל אחיד
    max_h = max(frame.shape[0] for frame in frames)
    max_w = max(frame.shape[1] for frame in frames)

    # מציאת הערך המקסימלי בכל הפריימים לצורך נרמול ל-8 ביט (0..255)
    global_max = max(float(np.max(frame)) for frame in frames)
    if global_max <= 0:
        global_max = 1.0

    # הגדרת מקודד הווידאו ל-MP4
    fourcc = cv2.VideoWriter.fourcc(*"mp4v")
    writer = cv2.VideoWriter(output_path, fourcc, float(fps), (max_w, max_h), isColor=True)

    if not writer.isOpened():
        raise RuntimeError(f"Failed to open video writer for path: {output_path}")

    for frame in frames:
        # נרמול ערכי הפיקסלים לטווח 0..255
        norm_frame = np.clip((frame / global_max) * 255.0, 0, 255).astype(np.uint8)

        # מירכוז הפריים בתוך קנבס בגודל אחיד (max_h, max_w)
        h, w = norm_frame.shape
        canvas = np.zeros((max_h, max_w), dtype=np.uint8)
        y_offset = (max_h - h) // 2
        x_offset = (max_w - w) // 2
        canvas[y_offset:y_offset + h, x_offset:x_offset + w] = norm_frame

        # המרה ל-3 ערוצים (BGR) לתאימות מלאה עם נגני וידאו כמו VLC
        bgr_frame = cv2.cvtColor(canvas, cv2.COLOR_GRAY2BGR)
        writer.write(bgr_frame)

    writer.release()