import re
from typing import List, Optional
import numpy as np
import cv2
from Plane import Plane

# קומפילציה חד-פעמית של הביטויים הרגולריים ברמת המודול
_NUMBER_PATTERN = re.compile(r"[-+]?\d*\.?\d+")
_LETTER_PATTERN = re.compile(r"[a-zA-Z]")


def load_planes_from_csv(csv_path: str, ignore_errors: bool = False) -> List[Optional[Plane]]:
    planes: List[Optional[Plane]] = []
    seen_data_row = False

    with open(csv_path, mode="r", encoding="utf-8") as f:
        for row_idx, line in enumerate(f):
            stripped = line.strip()

            if not stripped or stripped.startswith("#"):
                continue

            if _LETTER_PATTERN.search(stripped):
                # דילוג על שורת כותרת בתחילת הקובץ בלבד
                if not seen_data_row and "nan" not in stripped.lower() and "inf" not in stripped.lower():
                    seen_data_row = True
                    continue
                if ignore_errors:
                    print(f"Warning: Row {row_idx + 1} has invalid text. Using black frame.")
                    planes.append(None)
                    continue
                raise ValueError(f"Row {row_idx + 1} contains non-numeric characters.")

            seen_data_row = True

            try:
                # המרה ישירה למערך NumPy ללא יצירת רשימות פייתון זמניות
                values = np.fromiter(
                    (float(m.group(0)) for m in _NUMBER_PATTERN.finditer(stripped)),
                    dtype=np.float64,
                )
                if values.size == 0:
                    continue

                # אימות אינדקס השורה במידה וקיימת עמודת אינדקס (10 או 13 ערכים)
                if values.size in (10, 13):
                    idx_val = values[0]
                    if idx_val < 0 or not float(idx_val).is_integer():
                        raise ValueError(f"Row {row_idx + 1} has an invalid index: {idx_val}")
                    values = values[1:]

                if values.size == 9:
                    points = values.reshape((3, 3))
                elif values.size == 12:
                    points = values.reshape((4, 3))
                else:
                    raise ValueError(
                        f"Row {row_idx + 1} has {values.size} numbers. "
                        f"Expected 9 (3 points) or 12 (4 points)."
                    )

                planes.append(Plane(points))

            except ValueError as err:
                if ignore_errors:
                    print(f"Warning: Row {row_idx + 1} is invalid ({err}). Using black frame.")
                    planes.append(None)
                else:
                    raise

    return planes


def save_frames_to_mp4(frames: List[np.ndarray], output_path: str, fps: int = 30):
    if not frames:
        raise ValueError("Cannot create MP4 video from an empty list of frames.")

    # חישוב וקטורי של הגובה והרוחב המקסימליים במעבר אחד
    shapes = np.array([frame.shape for frame in frames])
    max_h, max_w = int(shapes[:, 0].max()), int(shapes[:, 1].max())

    # הגנה למקרה שכל השורות בקובץ היו פגומות (כולן בגודל 1x1)
    if max_h <= 1 and max_w <= 1:
        max_h, max_w = 16, 16

    # בדיקה אם כל הפריימים באותו גודל בדיוק
    same_shape = bool(np.all(shapes == [max_h, max_w]))

    if same_shape:
        # איחוד כל הפריימים למערך 3D אחד ונרמול וקטורי מלא במכה אחת
        stack = np.asarray(frames, dtype=np.float64)
        global_max = float(stack.max())
        scale = 255.0 / global_max if global_max > 0 else 0.0
        canvases = np.clip(stack * scale, 0, 255).astype(np.uint8)
    else:
        # הקצאת בלוק זיכרון תלת-ממדי אחד לכל הפריימים מראש ומירכוז לפני נרמול
        raw_canvases = np.zeros((len(frames), max_h, max_w), dtype=np.float64)
        y_offsets = (max_h - shapes[:, 0]) // 2
        x_offsets = (max_w - shapes[:, 1]) // 2

        for i, frame in enumerate(frames):
            h, w = shapes[i]
            y0, x0 = y_offsets[i], x_offsets[i]
            raw_canvases[i, y0:y0 + h, x0:x0 + w] = frame

        global_max = float(raw_canvases.max())
        scale = 255.0 / global_max if global_max > 0 else 0.0
        canvases = np.clip(raw_canvases * scale, 0, 255).astype(np.uint8)

    # יצירת אובייקט הווידאו
    fourcc = cv2.VideoWriter.fourcc(*"mp4v")
    writer = cv2.VideoWriter(output_path, fourcc, float(fps), (max_w, max_h), isColor=True)

    if not writer.isOpened():
        raise RuntimeError(f"Failed to open video writer for path: {output_path}")

    # שכפול וקטורי ל-3 ערוצים (BGR) וכתיבה סדרתית ל-VideoWriter
    bgr_frames = np.repeat(canvases[:, :, :, np.newaxis], 3, axis=3)
    for bgr_frame in bgr_frames:
        writer.write(bgr_frame)

    writer.release()