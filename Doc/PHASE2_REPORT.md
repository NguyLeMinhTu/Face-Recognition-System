# Báo Cáo Giai Đoạn 2

## 1. Tổng quan

Mục tiêu giai đoạn 2 là xây dựng một prototype nhận diện khuôn mặt realtime trên CPU: tải model ONNX, phát hiện mặt, trích landmarks và embedding, vẽ overlay trên ảnh camera, và hỗ trợ enroll/so khớp đơn giản.

Kết luận nhanh: Giai đoạn 2 đã hoàn thành phần POC end‑to‑end. Hệ thống hoạt động trên máy Windows với venv, có thể chạy realtime (hiển thị) và lưu embedding vào DB file-backed. Tuy nhiên để production cần bổ sung test, API, và cải thiện quản lý dependencies/venv.

## 2. Đã triển khai (file chính và công dụng)

- `app/core/face_recognizer.py` — Wrapper cho `insightface.FaceAnalysis`.
  - Chuẩn bị model từ `./models` và expose `analyze_bgr()` trả danh sách detections: `bbox`, `score`, `landmarks`, `embedding`.
- `app/core/face_database.py` — File-backed DB lưu embedding dưới `data/known_faces/<id>.npy` và index `index.json`.
  - `add(person_id, embedding)`, `get_embedding`, `list_ids`, `find_best(embedding)` (cosine similarity).
- `app/utils/drawing_utils.py` — Hàm tiện ích vẽ: `draw_bbox`, `draw_landmarks`, `draw_label`, `save_image`.
- `scripts/webcam_recognize.py` — Runner realtime và enroll.
  - Options: `--display`, `--frames`, `--name`, `--auto-enroll`, `--threshold`.
  - Tương tác: nhấn `e` để enroll current face (yêu cầu `--name`), nhấn `q` để thoát.
  - Lưu ảnh đã chú thích và metadata per-frame (`tmp/webcam_recognize/annotated_*.jpg`, `meta_*.json`).
- `tests/test_video_utils.py`, `tests/webcam_test.py` — scripts phụ giúp test video/webcam I/O.
- `data/known_faces/` — nơi lưu embeddings sau khi enroll.
- `config/development.yaml` — cấu hình phát triển, có trường `model.local_path: "./models/buffalo_s"`.

## 3. Cách chạy (quick start)

Lưu ý: chạy trong virtualenv dự án (`d:/FACE/Backend/venv312`).

- Chạy realtime display (interactive):

```powershell
d:/FACE/Backend/venv312/Scripts/python.exe d:/FACE/Backend/scripts/webcam_recognize.py --display --frames 0 --name alice
# Nhấn 'e' để enroll (lưu embedding cho 'alice'), nhấn 'q' để thoát
```

- Enroll tự động (non-interactive):

```powershell
d:/FACE/Backend/venv312/Scripts/python.exe d:/FACE/Backend/scripts/webcam_recognize.py --frames 1 --auto-enroll --name bob
```

- Chạy không hiển thị (lưu mỗi frame):

```powershell
d:/FACE/Backend/venv312/Scripts/python.exe d:/FACE/Backend/scripts/webcam_recognize.py --frames 3
```

Kết quả lưu ở `d:/FACE/Backend/tmp/webcam_recognize/` và embeddings trong `d:/FACE/Backend/data/known_faces/`.

## 4. Các lưu ý kỹ thuật & troubleshooting

- Dependency conflicts: trên cùng một venv có thể xảy ra xung đột giữa `numpy` phiên bản cũ (1.24.x) cần cho `insightface` và `opencv`/các gói khác. Hiện POC dùng tổ hợp đã kiểm chứng: `numpy==1.24.4` và `opencv-python==4.8.1.78`.
- Nếu bạn cần giữ các package khác (ví dụ `streamlit`, `tensorflow`), nên tạo venv riêng cho realtime/POC hoặc containerize để tránh xung đột.
- Nếu `cv2.imshow` báo lỗi "function is not implemented", nghĩa là headless OpenCV đang cài — cài `opencv-python` thay vì `opencv-python-headless` để có GUI trên Windows.

## 5. Độ hoàn thiện & đề xuất tiếp theo

- Giai đoạn 2 — POC: **Hoàn thành** cho mục tiêu phát triển & demo.
- Để chuyển sang bản dùng được (production/dev handoff), đề xuất ưu tiên:
  1. Thêm unit/integration tests cho `face_recognizer` (mocked) và `face_database`.
 2. Tạo CLI/Service riêng cho enroll/delete/list (ví dụ `scripts/enroll.py`) và endpoint HTTP (FastAPI) cho detect/enroll.
 3. Hỗ trợ multi-embedding per-id, index hiệu năng (FAISS) nếu DB lớn.
 4. CI job (tests + lint) và README hướng dẫn cài env tách biệt (dev vs. runtime) hoặc `Dockerfile` cho runtime.

## 6. Tài liệu tham khảo nhanh (file và lệnh)

- Files: `app/core/face_recognizer.py`, `app/core/face_database.py`, `app/utils/drawing_utils.py`, `scripts/webcam_recognize.py`, `config/development.yaml`.
- Run (reproduce):
  - Activate venv: `d:/FACE/Backend/venv312/Scripts/Activate.ps1` (PowerShell) hoặc run Python directly from venv.
  - Start realtime: see commands ở phần 3.

---

Nếu bạn muốn, tôi có thể tiếp tục và thực hiện một trong các mục ưu tiên ở phần 5 ngay bây giờ (ví dụ: thêm `scripts/enroll.py` CLI, hoặc thêm `--show-enroll-notification` khi enroll thành công, hoặc viết vài unit tests). Chỉ định mục bạn muốn tôi làm tiếp.

## 7. Trạng Thái Hoàn Thành (100%)

- **Tiến độ:** |████████████████████| **100%**
- **Tóm tắt:** Tất cả các mục cốt lõi của Phase 2 đã hoàn thành cho mục tiêu POC: tải model, phát hiện, trích embedding, vẽ overlay, enroll và lưu embedding vào DB file-backed. Các file chính đã được tạo và cập nhật theo kế hoạch trong `GIAIDOAN.md` (Phase 0, Phase 1, Phase 2).
- **Tương quan với `GIAIDOAN.md`:** tôi đã kiểm tra nội dung `GIAIDOAN.md` và đối chiếu các mục; Phase 0, Phase 1 và phần core của Phase 2 đã hoàn thành như báo cáo ở trên (model `buffalo_s` được dùng làm mặc định cho CPU-first POC). `GIAIDOAN.md` cũng liệt kê các bước tiếp theo (Phase 3/4) mà hệ thống hiện chưa thực hiện.
- **Những thay đổi nhỏ gần đây:** cập nhật giao diện overlay (`app/utils/drawing_utils.py`) để dùng tông **xanh dương** cho bounding box / landmarks / label / confidence bar, và cập nhật `scripts/webcam_recognize.py` để sử dụng tông màu này. Test script mẫu `tests/test_drawing_utils.py` sẵn sàng để kiểm tra nhanh.
- **Gợi ý tiếp theo (ưu tiên):**
  - Thêm unit tests cho `face_recognizer` và `face_database`.
  - Viết endpoint FastAPI cho detect/enroll.
  - Hộp công cụ deploy (Dockerfile) và CI (tests + lint).

---

Ghi chú: nếu bạn muốn, tôi sẽ tiếp tục ngay để hiện thực hoá một trong các mục ưu tiên trên (ví dụ: tạo `scripts/enroll.py`, viết vài unit tests, hoặc đóng gói Docker). Chỉ cần nói tên tác vụ và tôi sẽ bắt tay vào thực hiện.
