"""Visual test for drawing utilities.
Generates a blank image, draws a stylized bbox, landmarks, label and confidence bar,
and writes `tmp/test_drawing_output.jpg` for manual inspection.
"""
import os
import cv2
import numpy as np

from utils.drawing_utils import draw_bbox, draw_landmarks, draw_label, draw_confidence_bar, save_image


def main():
    os.makedirs('tmp', exist_ok=True)
    img = np.zeros((480, 640, 3), dtype=np.uint8)
    img[:] = (30, 30, 40)

    bbox = (180, 100, 460, 380)
    landmarks = [(260, 220), (340, 220), (300, 260), (270, 300), (330, 300)]
    label = "MinhTu (0.92) M 27"
    score = 0.92

    draw_bbox(img, bbox, color=(14, 215, 120), thickness=2)
    draw_landmarks(img, landmarks)
    draw_label(img, bbox, label, bgcolor=(8, 8, 8), fgcolor=(240, 240, 240))
    draw_confidence_bar(img, bbox, score, bar_color=(0, 200, 120))

    out = 'tmp/test_drawing_output.jpg'
    save_image(out, img)
    print('WROTE', out)


if __name__ == '__main__':
    main()
