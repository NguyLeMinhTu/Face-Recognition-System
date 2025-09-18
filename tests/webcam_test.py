import cv2
import argparse
from pathlib import Path

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--device', type=int, default=0)
    p.add_argument('--frames', type=int, default=5)
    p.add_argument('--display', action='store_true')
    p.add_argument('--outdir', type=str, default='d:/FACE/Backend/tmp/webcam')
    args = p.parse_args()

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    cap = cv2.VideoCapture(args.device)
    if not cap.isOpened():
        print('WEBCAM_OPEN_FAILED')
        return 2

    saved = 0
    try:
        while saved < args.frames:
            ret, frame = cap.read()
            if not ret:
                break
            outpath = outdir / f'frame_{saved:03d}.jpg'
            cv2.imwrite(str(outpath), frame)
            print('SAVED', outpath)
            saved += 1
            if args.display:
                cv2.imshow('webcam', frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
    finally:
        cap.release()
        if args.display:
            cv2.destroyAllWindows()

    print('FRAMES_SAVED', saved)

if __name__ == '__main__':
    raise SystemExit(main())
