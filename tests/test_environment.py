"""Run basic environment checks: imports and a tiny model prepare (CPU).
This does not process images; it only ensures libraries can be imported and model can be prepared.
"""
import sys

def check_imports():
    try:
        import insightface
        import cv2
        import numpy as np
        import onnxruntime
        print("Imports OK: insightface, cv2, numpy, onnxruntime")
    except Exception as e:
        print("Import error:", e)
        sys.exit(2)


def check_model_prepare():
    try:
        from insightface.app import FaceAnalysis
        app = FaceAnalysis(name='buffalo_s')
        app.prepare(ctx_id=-1)
        print("Model prepare OK (buffalo_s, CPU)")
    except Exception as e:
        print("Model prepare failed:", e)
        sys.exit(3)


if __name__ == '__main__':
    check_imports()
    check_model_prepare()
