import cv2
from typing import Iterator


def frames_from_video(path: str) -> Iterator:
    """Yield frames from a video file (BGR, as returned by OpenCV).

    Usage:
        for frame in frames_from_video('sample.mp4'):
            # process frame (OpenCV BGR image)
            pass
    """
    cap = cv2.VideoCapture(path)
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            yield frame
    finally:
        cap.release()
