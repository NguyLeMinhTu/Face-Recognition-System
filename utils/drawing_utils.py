'''
Tác dụng: Các hàm tiện ích để vẽ bounding boxes và landmarks trên ảnh.

Chức năng:
- draw_bbox: vẽ bounding box có bóng đổ và góc bo mềm mại
- draw_landmarks: vẽ điểm landmark với viền trắng để dễ nhìn
- draw_label: nhãn bán trong suốt với bóng chữ
- draw_confidence_bar: thanh hiển thị độ tin cậy
- save_image: lưu ảnh
'''

import cv2
import numpy as np
from typing import Sequence, Tuple


def _clip(v, lo, hi):
    return max(lo, min(hi, v))


def _rounded_rect(img, pt1, pt2, color, thickness=2, radius=12, alpha_fill=0.0):
    """Draw rounded rectangle with optional translucent fill using overlay blending."""
    x1, y1 = pt1
    x2, y2 = pt2
    radius = int(max(0, min(radius, (x2 - x1) // 4, (y2 - y1) // 4)))
    overlay = img.copy()

    # fill
    if alpha_fill > 0:
        cv2.rectangle(overlay, (x1 + radius, y1), (x2 - radius, y2), color, -1)
        cv2.rectangle(overlay, (x1, y1 + radius), (x2, y2 - radius), color, -1)
        # corners
        cv2.circle(overlay, (x1 + radius, y1 + radius), radius, color, -1, cv2.LINE_AA)
        cv2.circle(overlay, (x2 - radius, y1 + radius), radius, color, -1, cv2.LINE_AA)
        cv2.circle(overlay, (x1 + radius, y2 - radius), radius, color, -1, cv2.LINE_AA)
        cv2.circle(overlay, (x2 - radius, y2 - radius), radius, color, -1, cv2.LINE_AA)
        cv2.addWeighted(overlay, alpha_fill, img, 1 - alpha_fill, 0, img)

    # border
    cv2.line(img, (x1 + radius, y1), (x2 - radius, y1), color, thickness, cv2.LINE_AA)
    cv2.line(img, (x1 + radius, y2), (x2 - radius, y2), color, thickness, cv2.LINE_AA)
    cv2.line(img, (x1, y1 + radius), (x1, y2 - radius), color, thickness, cv2.LINE_AA)
    cv2.line(img, (x2, y1 + radius), (x2, y2 - radius), color, thickness, cv2.LINE_AA)
    if radius > 0:
        cv2.ellipse(img, (x1 + radius, y1 + radius), (radius, radius), 180, 0, 90, color, thickness, cv2.LINE_AA)
        cv2.ellipse(img, (x2 - radius, y1 + radius), (radius, radius), 270, 0, 90, color, thickness, cv2.LINE_AA)
        cv2.ellipse(img, (x1 + radius, y2 - radius), (radius, radius), 90, 0, 90, color, thickness, cv2.LINE_AA)
        cv2.ellipse(img, (x2 - radius, y2 - radius), (radius, radius), 0, 0, 90, color, thickness, cv2.LINE_AA)


def draw_bbox(img, bbox: Sequence[float], color=(255, 0, 0), thickness=2, radius: int = 12):
    """Draw a prettier bounding box: soft drop shadow, rounded border and subtle fill."""
    x1, y1, x2, y2 = map(int, bbox)
    h, w = img.shape[:2]
    x1 = _clip(x1, 0, w - 1)
    x2 = _clip(x2, 0, w - 1)
    y1 = _clip(y1, 0, h - 1)
    y2 = _clip(y2, 0, h - 1)

    # soft shadow (subtle)
    overlay = img.copy()
    shadow_color = (0, 0, 0)
    off = max(3, thickness)
    cv2.rectangle(overlay, (x1 + off, y1 + off), (x2 + off, y2 + off), shadow_color, -1)
    cv2.GaussianBlur(overlay, (11, 11), 0, dst=overlay)
    cv2.addWeighted(overlay, 0.12, img, 0.88, 0, img)

    # light translucent fill to reduce contrast with background
    fill_color = (int(color[0] * 0.9), int(color[1] * 0.9), int(color[2] * 0.9))
    _rounded_rect(img, (x1, y1), (x2, y2), fill_color, thickness=2, radius=radius, alpha_fill=0.04)


def draw_landmarks(img, landmarks: Sequence[Tuple[float, float]], color=(255, 0, 0)):
    """Draw small landmark dots with a white halo and thin dark outline (blue by default)."""
    for (x, y) in landmarks:
        cx, cy = int(round(x)), int(round(y))
        # outer halo
        cv2.circle(img, (cx, cy), 4, (255, 255, 255), -1, cv2.LINE_AA)
        # main dot
        cv2.circle(img, (cx, cy), 2, color, -1, cv2.LINE_AA)
        # thin outline
        cv2.circle(img, (cx, cy), 3, (20, 20, 20), 1, cv2.LINE_AA)


def save_image(path: str, img) -> None:
    cv2.imwrite(path, img)


def _get_text_size(text: str, font_scale: float = 0.5, thickness: int = 1):
    font = cv2.FONT_HERSHEY_SIMPLEX
    (w, h), baseline = cv2.getTextSize(text, font, font_scale, thickness)
    return (w, h + baseline)


def draw_label(img, bbox: Sequence[float], label: str, bgcolor=(255, 0, 0), fgcolor=(255, 255, 255)):
    """Draw a rounded, semi-transparent label above the bbox with an embossed shadowed text."""
    x1, y1, x2, y2 = map(int, bbox)
    font = cv2.FONT_HERSHEY_SIMPLEX
    scale = 0.5
    thickness = 1
    (w, h) = _get_text_size(label, scale, thickness)
    pad_x = 8
    pad_y = 6

    rect_w = w + pad_x * 2
    rect_h = h + pad_y * 2
    rect_x1 = x1
    rect_x2 = x1 + rect_w
    rect_y2 = max(0, y1)
    rect_y1 = max(0, rect_y2 - rect_h)

    # solid but slightly translucent background (use lower alpha for clarity)
    bg_col = tuple(int(c) for c in bgcolor)
    _rounded_rect(img, (rect_x1, rect_y1), (rect_x2, rect_y2), bg_col, thickness=1, radius=6, alpha_fill=0.6)

    # crisp text (no heavy shadow) for readability
    text_org = (rect_x1 + pad_x, rect_y2 - pad_y - 2)
    cv2.putText(img, label, text_org, font, scale, fgcolor, thickness, cv2.LINE_AA)


def draw_confidence_bar(img, bbox: Sequence[float], score: float, bar_color=(255, 0, 0)):
    """Draw a horizontal gradient confidence bar under the bbox representing score (0..1)."""
    x1, y1, x2, y2 = map(int, bbox)
    w = max(20, x2 - x1)
    bar_h = max(6, int(w * 0.035))
    gap = 6
    bar_x1 = x1
    bar_y1 = min(img.shape[0] - bar_h - 1, y2 + gap)
    bar_x2 = x1 + w

    # background rounded bar (dark translucent)
    _rounded_rect(img, (bar_x1, bar_y1), (bar_x2, bar_y1 + bar_h), (30, 30, 30), thickness=1, radius=6, alpha_fill=0.85)

    # filled portion
    filled_w = int(_clip(score, 0.0, 1.0) * w)
    if filled_w > 0:
        # create gradient for the filled portion
        grad = np.linspace(0, 1, filled_w)
        # filled solid color (single tone) for clarity in small bars
        col = (int(bar_color[0]), int(bar_color[1]), int(bar_color[2]))
        cv2.rectangle(img, (bar_x1, bar_y1 + 1), (bar_x1 + filled_w, bar_y1 + bar_h - 1), col, -1)

