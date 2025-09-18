'''
Tác dụng: Chạy nhận diện khuôn mặt từ webcam, vẽ bounding box, landmarks, nhãn (nếu có trong DB),
        và lưu các khung đã chú thích cùng với siêu dữ liệu vào thư mục đầu ra.

Ví dụ sử dụng:
    python scripts/webcam_recognize.py --device 0 --frames 10 --outdir ./output --display
    => Chạy nhận diện khuôn mặt từ webcam (thiết bị 0), lưu 10 khung đã chú thích vào ./output, hiển thị cửa sổ video.

    python scripts/webcam_recognize.py --device 0 --frames 0 --outdir ./output --display
    => Chạy nhận diện khuôn mặt từ webcam (thiết bị 0), lưu các khung đã chú thích vào ./output cho đến khi nhấn 'q', hiển thị cửa sổ video.

    python scripts/webcam_recognize.py --device 0 --frames 0 --outdir ./output --name alice --auto-enroll --display
    => Chạy nhận diện khuôn mặt từ webcam (thiết bị 0), tự động đăng ký khuôn mặt đầu tiên phát hiện được dưới tên "alice", lưu các khung đã chú thích vào ./output cho đến khi nhấn 'q', hiển thị cửa sổ video.
'''

import sys
from pathlib import Path
import argparse
import json

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from utils.drawing_utils import draw_bbox, draw_landmarks, save_image, draw_label, draw_confidence_bar
from core.face_recognizer import FaceRecognizer
from core.face_database import FaceDatabase

try:
    import yaml
except Exception:
    yaml = None

import cv2
import numpy as np


def load_config(path: str = 'config/development.yaml'):
    p = Path(path)
    if not p.exists() or yaml is None:
        return {'model': {'name': 'buffalo_s', 'local_path': './models/buffalo_s'}}
    with p.open('r', encoding='utf-8') as f:
        cfg = yaml.safe_load(f)
    return cfg


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--device', type=int, default=0)
    p.add_argument('--frames', type=int, default=5, help='Số khung để xử lý (0 = không giới hạn, nhấn "q" để thoát)')
    p.add_argument('--outdir', type=str, default='d:/FACE/Backend/tmp/webcam_recognize')
    p.add_argument('--name', type=str, default=None, help='Tên để sử dụng khi đăng ký một khuôn mặt')
    p.add_argument('--auto-enroll', action='store_true', help='Tự động đăng ký khuôn mặt đầu tiên phát hiện được bằng cách sử dụng --name')
    p.add_argument('--threshold', type=float, default=0.4, help='Ngưỡng điểm khớp để hiển thị nhãn')
    p.add_argument('--display', action='store_true')
    args = p.parse_args()

    cfg = load_config()
    model_cfg = cfg.get('model', {})
    model_name = model_cfg.get('name', 'buffalo_s')
    local_path = model_cfg.get('local_path')

    # Normalize local_path: if user set local_path to './models/<model_name>' or
    # similar, return the parent before 'models' so downstream code doesn't
    # produce duplicated paths like './models/buffalo_s/models/buffalo_s'.
    def _normalize_model_root(lp: str | None, mname: str) -> str | None:
        if not lp:
            return None
        try:
            p = Path(lp)
            p_res = p.resolve()
            parts = [part.lower() for part in p_res.parts]
            seq = ['models', mname.lower()]
            for i in range(len(parts) - 1):
                if parts[i:i+2] == seq:
                    # build root from parts before 'models'
                    if i == 0:
                        return str(Path(p_res.anchor or '.'))
                    return str(Path(*p_res.parts[:i]))
            return str(p_res)
        except Exception:
            return lp

    local_path = _normalize_model_root(local_path, model_name)

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    # optional face DB (if empty, matching will be skipped)
    db = FaceDatabase()

    # initialize recognizer
    try:
        recognizer = FaceRecognizer(model_name=model_name, device='cpu', local_path=local_path)
    except Exception as e:
        print('MODEL_INIT_FAILED', e)
        return 2

    cap = cv2.VideoCapture(args.device)
    if not cap.isOpened():
        print('WEBCAM_OPEN_FAILED')
        return 3

    saved = 0
    try:
        # if args.frames == 0, run until user presses 'q'
        while args.frames == 0 or saved < args.frames:
            ret, frame = cap.read()
            if not ret:
                break
            # analyze frame (frame is BGR)
            try:
                detections = recognizer.analyze_bgr(frame)
            except Exception as e:
                print('ANALYZE_ERROR', e)
                detections = []

            # draw detections
            for det in detections:
                bbox = det.get('bbox')
                if bbox:
                    draw_bbox(frame, bbox)
                lms = det.get('landmarks')
                if lms:
                    draw_landmarks(frame, lms)
                emb = det.get('embedding')
                label = None
                score = None
                if emb is not None:
                    try:
                        res = db.find_best(np.array(emb, dtype=float))
                        if res is not None:
                            label, score = res
                    except Exception:
                        label = None
                if label is not None and score is not None and score >= args.threshold:
                    # include gender/age if available in detection metadata
                    gender = det.get('gender')
                    age = det.get('age')
                    extra = ''
                    if gender is not None or age is not None:
                        parts = []
                        if gender is not None:
                            parts.append(str(gender))
                        if age is not None:
                            parts.append(str(age))
                        extra = ' ' + '/'.join(parts)
                    lbl = f"{label} ({score:.2f}){extra}"
                    # choose blue background for label and blue bar to match theme
                    bg = (255, 0, 0)
                    fg = (255, 255, 255)
                    draw_label(frame, bbox, lbl, bgcolor=bg, fgcolor=fg)
                    # draw a blue confidence bar
                    try:
                        draw_confidence_bar(frame, bbox, float(score), bar_color=(255, 0, 0))
                    except Exception:
                        pass

            # enrollment: if auto-enroll requested, save first embedding under --name
            if args.auto_enroll and args.name and saved == 0:
                # find first detection with embedding
                for det in detections:
                    emb = det.get('embedding')
                    if emb is not None:
                        try:
                            db.add(args.name, np.array(emb, dtype=float))
                            print('AUTO_ENROLLED', args.name)
                        except Exception as e:
                            print('ENROLL_FAILED', e)
                        break

            img_path = outdir / f'annotated_{saved:03d}.jpg'
            save_image(str(img_path), frame)

            meta = {
                'frame': saved,
                'detections': detections,
            }
            (outdir / f'meta_{saved:03d}.json').write_text(json.dumps(meta, ensure_ascii=False, indent=2))

            print('SAVED', img_path)
            saved += 1
            if args.display:
                cv2.imshow('Face Detection', frame)
                # waitKey(1) returns -1 if no key pressed; check for 'q' to quit and 'e' to enroll
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    print('USER_QUIT')
                    break
                if key == ord('e') and args.name:
                    # enroll current frame's first embedding
                    for det in detections:
                        emb = det.get('embedding')
                        if emb is not None:
                            try:
                                db.add(args.name, np.array(emb, dtype=float))
                                print('ENROLLED', args.name)
                            except Exception as e:
                                print('ENROLL_FAILED', e)
                            break
    finally:
        cap.release()
        if args.display:
            cv2.destroyAllWindows()

    print('FRAMES_PROCESSED', saved)


if __name__ == '__main__':
    raise SystemExit(main())
