"""Công cụ đơn giản để tải xuống các gói mô hình InsightFace được sử dụng bởi dự án.
Sử dụng: python scripts/download_models.py --name buffalo_s
"""
import argparse
from insightface.app import FaceAnalysis


def download_model(name: str):
    print(f"Preparing model '{name}' (will download if missing)")
    app = FaceAnalysis(name=name)
    # prepare will download model files to the cache if not present
    app.prepare(ctx_id=-1)
    print("Model prepared (download complete if it was missing).")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--name", default="buffalo_s", help="Model pack name to download")
    args = parser.parse_args()
    download_model(args.name)


if __name__ == "__main__":
    main()
