#!/usr/bin/env python3
""" Công cụ đăng ký khuôn mặt.

Tham số:
    --image: Đường dẫn đến tệp hình ảnh để đăng ký
    --dir: Đường dẫn đến thư mục hình ảnh để đăng ký
    --name: Tên của người để đăng ký (bắt buộc)
    ---model: Tên mô hình insightface, ghi đè cấu hình
    --local-path: Đường dẫn đến mô hình cục bộ
    --webcam: Sử dụng webcam để đăng ký
    --device: ID thiết bị webcam

Ví dụ sử dụng:
    python scripts/enroll.py --image ./test_images/img1.jpg --name alice 
    => Đăng ký khuôn mặt từ một tệp hình ảnh.

    python scripts/enroll.py --dir ./photos/alice --name alice
    => Đăng ký khuôn mặt từ một thư mục hình ảnh.
"""
import sys
from pathlib import Path
import argparse
import json

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.core.face_recognizer import FaceRecognizer
from app.core.face_database import FaceDatabase
import cv2
import numpy as np

try:
    import yaml
except Exception:
    yaml = None


def iter_images(path: Path):
    if path.is_file():
        yield path
    else:
        for p in sorted(path.glob('*')):
            if p.suffix.lower() in ['.jpg', '.jpeg', '.png', '.bmp']:
                yield p


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--image', type=str, default=None, help='Đường dẫn đến tệp hình ảnh để đăng ký')
    p.add_argument('--dir', type=str, default=None, help='Đường dẫn đến thư mục hình ảnh để đăng ký')
    p.add_argument('--name', type=str, required=True, help='Tên của người để đăng ký')
    p.add_argument('--model', type=str, default=None, help='Tên mô hình insightface, ghi đè cấu hình')
    p.add_argument('--local-path', type=str, default=None, help='Đường dẫn đến mô hình cục bộ')
    p.add_argument('--webcam', action='store_true', help='Sử dụng webcam để đăng ký')
    p.add_argument('--device', type=int, default=0, help='ID thiết bị webcam')
    p.add_argument('--frames', type=int, default=5, help='Số khung hình để xử lý từ webcam (0 = không giới hạn)')
    p.add_argument('--display', action='store_true', help='Hiển thị cửa sổ webcam')
    args = p.parse_args()

    # load defaults from config if present
    def load_config(path: str = 'config/development.yaml'):
        pth = Path(path)
        if not pth.exists() or yaml is None:
            return {'model': {'name': 'buffalo_s', 'local_path': './models/buffalo_s'}}
        with pth.open('r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    cfg = load_config()
    model_cfg = cfg.get('model', {})
    model_name = args.model or model_cfg.get('name', 'buffalo_s')
    local_path = args.local_path or model_cfg.get('local_path', './models/buffalo_s')

    # initialize recognizer and db
    try:
        recognizer = FaceRecognizer(model_name=model_name, device='cpu', local_path=local_path)
    except Exception as e:
        print('MODEL_INIT_FAILED', e)
        return 2

    db = FaceDatabase()

    enrolled = 0

    # webcam enrollment
    if args.webcam:
        cap = cv2.VideoCapture(args.device)
        if not cap.isOpened():
            print('WEBCAM_OPEN_FAILED')
            return 3

        saved = 0
        try:
            while args.frames == 0 or saved < args.frames:
                ret, frame = cap.read()
                if not ret:
                    break
                try:
                    dets = recognizer.analyze_bgr(frame)
                except Exception as e:
                    print('ANALYZE_ERROR', e)
                    dets = []

                # display simple info
                if args.display:
                    disp = frame.copy()
                    # draw boxes for visibility if any
                    for det in dets:
                        bbox = det.get('bbox')
                        if bbox:
                            x1, y1, x2, y2 = [int(v) for v in bbox]
                            cv2.rectangle(disp, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    cv2.imshow('Enroll', disp)

                # allow manual enrollment by pressing 'e' (when display is enabled)
                key = None
                if args.display:
                    key = cv2.waitKey(1) & 0xFF
                    if key == ord('q'):
                        print('USER_QUIT')
                        break

                # if display disabled, just enroll first detection each frame
                if dets:
                    # take first embedding
                    emb = dets[0].get('embedding')
                    if emb is None:
                        print('NO_EMBED')
                    else:
                        do_enroll = False
                        if args.display and key == ord('e'):
                            do_enroll = True
                        elif not args.display:
                            do_enroll = True

                        if do_enroll:
                            try:
                                db.add(args.name, np.array(emb, dtype=float))
                                enrolled += 1
                                print('ENROLLED', args.name, f'frame#{saved}')
                            except Exception as e:
                                print('ENROLL_FAILED', e)

                saved += 1
        finally:
            cap.release()
            if args.display:
                cv2.destroyAllWindows()

        print('TOTAL_ENROLLED', enrolled)
        return 0

    # image/dir enrollment (existing behavior)
    imgs = []
    if args.image:
        imgs.append(Path(args.image))
    if args.dir:
        imgs.extend(list(iter_images(Path(args.dir))))
    if len(imgs) == 0:
        print('No images provided. Use --image, --dir or --webcam')
        return 2

    for imgp in imgs:
        img = cv2.imread(str(imgp))
        if img is None:
            print('SKIP', imgp)
            continue
        try:
            dets = recognizer.analyze_bgr(img)
        except Exception as e:
            print('ANALYZE_ERROR', e)
            continue
        if not dets:
            print('NO_FACE', imgp)
            continue
        emb = dets[0].get('embedding')
        if emb is None:
            print('NO_EMBED', imgp)
            continue
        try:
            db.add(args.name, np.array(emb, dtype=float))
            enrolled += 1
            print('ENROLLED', args.name, imgp)
        except Exception as e:
            print('ENROLL_FAILED', e)

    print('TOTAL_ENROLLED', enrolled)


if __name__ == '__main__':
    raise SystemExit(main())
