# Hướng Dẫn Chạy  - Enroll & Nhận Diện

Tài liệu này hướng dẫn cách chạy các script enroll (đăng ký khuôn mặt) và nhận diện mặt theo ba nguồn đầu vào: ảnh tĩnh (image), video (file video), và camera (webcam). Các lệnh ví dụ được viết cho PowerShell trên Windows và giả định bạn đang sử dụng virtual environment có Python tại `d:/FACE/Backend/venv312`.

## 0) Cài môi trường ảo (venv) và cài thư viện
Nếu bạn chưa có virtual environment cho dự án, tạo một venv trong thư mục dự án và cài các thư viện từ `requirements.txt` như sau (ví dụ cho PowerShell trên Windows). Thay `venv` bằng `venv312` nếu bạn muốn giữ tên cũ.

```powershell
# Chuyển tới thư mục dự án
cd d:/FACE/Backend

# Tạo virtual environment (tên 'venv' hoặc 'venv312')
python -m venv venv

# Kích hoạt venv (PowerShell)
& .\venv\Scripts\Activate.ps1

# Hoặc kích hoạt bằng đường dẫn tuyệt đối
& d:/FACE/Backend/venv/Scripts/Activate.ps1

# Cập nhật pip và cài các phụ thuộc của dự án
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

# Nếu bạn không muốn kích hoạt, có thể gọi python trực tiếp từ venv:
d:/FACE/Backend/venv/Scripts/python.exe scripts/enroll.py --help
```

Lưu ý:
- Nếu bạn gặp lỗi vì ExecutionPolicy khi chạy `Activate.ps1`, lệnh `Set-ExecutionPolicy` phía trên chỉ thay đổi phạm vi cho tiến trình hiện tại.
- Nếu cần GUI cho OpenCV trên Windows, đảm bảo `opencv-python` (không phải `opencv-python-headless`) được cài.

**Ghi chú chung**
- Kích hoạt virtualenv (PowerShell):

```powershell
# Nếu muốn kích hoạt:
& d:/FACE/Backend/venv312/Scripts/Activate.ps1
# Hoặc chạy Python trực tiếp từ venv:
# d:/FACE/Backend/venv312/Scripts/python.exe <script> [options]
```

- Thư mục dự án: `d:/FACE/Backend`
- Embeddings (DB file-backed) lưu trong: `d:/FACE/Backend/data/known_faces/`
- Ảnh và kết quả tạm lưu trong: `d:/FACE/Backend/tmp/`

---

## 1.Enroll từ Ảnh (Image)
Sử dụng `scripts/enroll.py` để đăng ký một người từ file ảnh hoặc một thư mục chứa ảnh.

- Enroll một file ảnh:

```powershell
# enroll.py: lưu embedding cho 'alice' từ một ảnh
d:/FACE/Backend/venv312/Scripts/python.exe d:/FACE/Backend/scripts/enroll.py --image d:/FACE/Backend/test_images/img1.jpg --name alice
```

- Enroll tất cả ảnh trong thư mục:

```powershell
# enroll mọi ảnh trong thư mục test_images với tên id 'bob'
d:/FACE/Backend/venv312/Scripts/python.exe d:/FACE/Backend/scripts/enroll.py --dir d:/FACE/Backend/test_images --name bob
```

Lưu ý: `scripts/enroll.py` sẽ in ra trạng thái cho mỗi ảnh: `ENROLLED: <name>`, `NO_FACE` hoặc `MULTIPLE_FACES`.

---

## 2. Enroll từ Video File
Bạn có thể enroll từ file video bằng cách chỉ định `--video` hoặc `--frames` để chỉ trích embedding từ một số frame.

```powershell
# Lấy 5 frame đầu từ file video và enroll làm 'charlie'
d:/FACE/Backend/venv312/Scripts/python.exe d:/FACE/Backend/scripts/enroll.py --video d:/path/to/video.mp4 --frames 5 --name charlie
```

Nếu không cung cấp `--name`, script có thể lưu các frame đã trích xuất nhưng sẽ không tạo entry embedding.

---

## 3. Enroll từ Webcam (Camera)
Script hỗ trợ webcam tương tác (mirroring theo `scripts/webcam_recognize.py`): hiển thị cửa sổ video và cho phép nhấn phím để enroll.

- Chạy interactive webcam (hiển thị):

```powershell
# Mở camera mặc định (device 0), hiển thị và cho phép nhấn 'e' để enroll
d:/FACE/Backend/venv312/Scripts/python.exe d:/FACE/Backend/scripts/enroll.py --webcam --display --device 0 --name dana
```

- Enroll tự động từ webcam (không hiển thị), chụp một frame và lưu embedding:

```powershell
# Chụp 1 frame và auto-enroll cho 'eve'
d:/FACE/Backend/venv312/Scripts/python.exe d:/FACE/Backend/scripts/enroll.py --webcam --frames 1 --auto-enroll --name eve
```

- Tùy chọn quan trọng:
  - `--device <n>`: chọn camera device index (mặc định `0`).
  - `--frames <n>`: số frame để grab (0 = liên tục cho đến khi nhấn 'q' hoặc 'e' khi display bật).
  - `--display`: bật `cv2.imshow` để tương tác.
  - `--auto-enroll`: khi bật sẽ tự enroll sau số frames chỉ định mà không cần phím.

---

## 4. Nhận diện (Recognition) – chạy realtime hoặc trên file
Sử dụng `scripts/webcam_recognize.py` cho nhận diện realtime hoặc chỉ định `--video`/`--image` nếu muốn chạy trên file.

- Nhận diện từ webcam (hiển thị bounding box, tên và confidence):

```powershell
d:/FACE/Backend/venv312/Scripts/python.exe d:/FACE/Backend/scripts/webcam_recognize.py --display --frames 0
# Nhấn 'e' để enroll face hiện tại (yêu cầu --name), 'q' để thoát
```

- Nhận diện một file ảnh:

```powershell
d:/FACE/Backend/venv312/Scripts/python.exe d:/FACE/Backend/scripts/webcam_recognize.py --image d:/FACE/Backend/test_images/img2.jpg
```

- Nhận diện một file video và lưu các frame chú thích:

```powershell
# Lưu 10 frame đã annotate vào tmp/webcam_recognize/
d:/FACE/Backend/venv312/Scripts/python.exe d:/FACE/Backend/scripts/webcam_recognize.py --video d:/path/to/video.mp4 --frames 10
```

Tùy chọn `--threshold` điều chỉnh ngưỡng cosine similarity để gán label (mặc định có thể set trong `config/development.yaml`).

---

## 5. Cấu hình & Mô hình
- Mặc định script sẽ đọc `config/development.yaml` nếu có để lấy `model.local_path` (ví dụ `./models/buffalo_s`) và các tham số khác.
- Nếu bạn muốn thay model dùng cho POC, chỉnh `config/development.yaml` hoặc truyền biến môi trường/option nếu script hỗ trợ.

---

## 6. Kiểm tra nhanh & Troubleshooting
- Nếu không thấy cửa sổ `cv2.imshow`, có thể bạn đang dùng `opencv-python-headless`. Cài `opencv-python` để có GUI trên Windows:

```powershell
# cài đặt vào venv
& d:/FACE/Backend/venv312/Scripts/python.exe -m pip install opencv-python
```

- Lỗi import `insightface`/model ONNX: kiểm tra `numpy` và `onnxruntime` phiên bản phù hợp (xem `Doc/PHASE2_REPORT.md` cho gợi ý phiên bản).
- Kiểm tra file `data/known_faces/index.json` để xác nhận embeddings đã được lưu.

---

## 7. Ví dụ tổng hợp (workflow)
1. Enroll Alice từ ảnh:

```powershell
& d:/FACE/Backend/venv312/Scripts/Activate.ps1
d:/FACE/Backend/venv312/Scripts/python.exe d:/FACE/Backend/scripts/enroll.py --image d:/FACE/Backend/test_images/img1.jpg --name alice
```

2. Chạy nhận diện realtime và hiển thị:

```powershell
d:/FACE/Backend/venv312/Scripts/python.exe d:/FACE/Backend/scripts/webcam_recognize.py --display --frames 0
```

3. Kiểm tra rằng `data/known_faces/alice.npy` tồn tại và `data/known_faces/index.json` chứa khóa `alice`.

---

Nếu bạn muốn, tôi có thể bổ sung hướng dẫn bằng ảnh chụp màn hình, ví dụ cấu hình `development.yaml`, hoặc viết lệnh PowerShell để export/backup `data/known_faces/`.
