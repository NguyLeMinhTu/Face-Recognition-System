# Báo cáo Giai đoạn 0 - Chuẩn bị Môi trường & Cài đặt Cơ bản

## 1. Mục tiêu

Thiết lập môi trường phát triển, cài dependencies cơ bản và tải model mẫu để đảm bảo project có thể chạy trên máy local (CPU-first). 

## 2. Các file đã tạo
- `requirements.txt` - danh sách dependencies cơ bản (CPU-first)
- `setup_environment.ps1` - PowerShell script tạo virtual environment và cài packages
- `scripts/download_models.py` - script helper để tải model InsightFace
- `test_environment.py` - script kiểm tra import và chuẩn bị model
- `config/development.yaml` - config mặc định (device: cpu)

## 3. Các bước thực hiện

1. Tạo và sửa `requirements.txt` để liệt kê các package cần thiết.
2. Viết `setup_environment.ps1` để tạo venv và cài packages trên Windows.
3. Viết `scripts/download_models.py` để tải model pack (`buffalo_s`).
4. Viết `test_environment.py` để kiểm tra import cốt lõi và gọi `FaceAnalysis.prepare(ctx_id=-1)`.
5. Chạy `pip install -r requirements.txt` trong virtualenv `venv312`.
6. Khi gặp lỗi liên quan tới công cụ biên dịch, cài Visual C++ Build Tools (đã cài bằng Chocolatey trên máy).
7. Hạ cấp `numpy` xuống `1.24.4` để giải quyết lỗi binary incompatibility.
8. Chạy lại script tải model — quá trình tải ban đầu gặp `IncompleteRead` do mạng, sau khi retry model `buffalo_s` được tải và chuẩn bị thành công.

## 4. Vấn đề đã gặp và cách khắc phục

- Lỗi: `Microsoft Visual C++ 14.0 or greater is required` khi pip cố build một số phần native.
  - Khắc phục: Cài `visualstudio2022buildtools` bằng Chocolatey hoặc tải về từ trang Microsoft và chọn workload **C++ build tools**.

- Lỗi: `numpy.dtype size changed, may indicate binary incompatibility` (do versions không tương thích giữa numpy và một số wheel).
  - Khắc phục: Hạ cấp `numpy` xuống `1.24.4` (tương thích với một số binary hiện có trên hệ thống). Lưu ý: downgrade có thể gây cảnh báo xung đột với các package khác (tensorflow, opencv versions). Nếu cần, cân nhắc tạo venv mới với Python version phù hợp.

- Lỗi: `IncompleteRead` khi tải model (kết nối mạng bị gián đoạn)
  - Khắc phục: retry download bằng `scripts/download_models.py`; nếu vẫn thất bại, tải file zip model thủ công từ trang releases của InsightFace và giải nén vào `C:\Users\<user>/.insightface/models/<model_name>`.

## 5. Kết quả kiểm tra

- `pip install -r requirements.txt` đã cài thành công vào `venv312`.
- `test_environment.py` xác nhận imports OK sau khi hạ cấp `numpy`.
- `scripts/download_models.py --name buffalo_s` đã tải và chuẩn bị model `buffalo_s` thành công; các file `.onnx` được nhận diện và ONNX Runtime dùng CPUExecutionProvider.

## 6. Khuyến nghị và bước tiếp theo

1. Đánh dấu Giai đoạn 0 hoàn thành trong `GIAIDOAN.md`.
2. Tạo file POC `basic_detection.py` để: load image, detect face, in ra bbox và embedding cho một ảnh mẫu. Chạy POC để xác nhận pipeline end-to-end.
3. Cân nhắc tạo venv mới nếu cần tương thích package (ví dụ dùng Python 3.10/3.11) để tránh xung đột version.
4. Thêm hướng dẫn setup ngắn vào `README.md` (Windows prerequisites: Visual C++ Build Tools, cách kích hoạt venv và các lệnh test).

---

Report generated: Giai đoạn 0 hoàn tất — môi trường hoạt động được trên CPU với `buffalo_s` model.
