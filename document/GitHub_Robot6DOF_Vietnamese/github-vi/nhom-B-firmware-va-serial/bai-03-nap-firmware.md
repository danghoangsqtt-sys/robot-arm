# Bài 3: Nạp Firmware và Giao Tiếp Serial Cơ Bản

## 🎯 Mục tiêu

- Tạo project PlatformIO và tổ chức đúng cấu trúc thư mục firmware
- Biên dịch (compile) firmware thành công, không lỗi
- Nạp (upload) firmware vào ESP32 thành công
- Kiểm chứng hoạt động phần cứng thông qua Serial Monitor

## 📦 Chuẩn bị

- Hệ thống phần cứng đã kết nối đúng theo Bài 2
- ESP32 đã cắm USB vào máy tính, COM port đã xác nhận
- Mã nguồn firmware (đã cung cấp sẵn)

## 📝 Các Bước Thực Hành

### Bước 1: Tạo project mới

1. Mở VS Code → nhấn biểu tượng PlatformIO (con kiến) ở thanh bên trái
2. Chọn "New Project" (hoặc Home → New Project)
3. Điền thông tin:
   - **Name**: `RobotArm`
   - **Board**: gõ "ESP32 Dev Module" và chọn kết quả
   - **Framework**: Arduino
4. Nhấn "Finish". Đợi PlatformIO tải các gói cần thiết (lần đầu có thể mất 5–10 phút)

### Bước 2: Tổ chức cấu trúc thư mục

```
RobotArm/
├── src/               ← thư mục chứa mã nguồn
│   └── main.cpp
├── include/           ← thư mục chứa file header
└── platformio.ini     ← file cấu hình project
```

### Bước 3: Cập nhật file `platformio.ini`

Mở file `platformio.ini`, xóa toàn bộ nội dung cũ, thay bằng:

```ini
[env:esp32dev]
platform       = espressif32
board          = esp32dev
framework      = arduino
monitor_speed  = 115200
upload_speed   = 921600
build_flags =
    -Os
    -DCORE_DEBUG_LEVEL=0
```

### Bước 4: Tạo các file mã nguồn

Trong thư mục `src/`, tạo các file:

| File | Chức năng |
|:---|:---|
| `config.h` | Cấu hình chung (chân I2C, bảng servo) |
| `pca9685.h` + `pca9685.cpp` | Driver điều khiển PCA9685 |
| `servo_ctrl.h` + `servo_ctrl.cpp` | Bộ điều khiển chuyển động servo |
| `cmd_parser.h` + `cmd_parser.cpp` | Bộ phân tích lệnh Serial |
| `main.cpp` | Chương trình chính |

> **Lưu ý**: Tất cả file `.h` và `.cpp` phải nằm trong cùng thư mục `src/`. Nếu để sai thư mục, trình biên dịch sẽ báo lỗi "file not found".

### Bước 5: Biên dịch (Compile/Build)

1. Trên status bar phía dưới VS Code, nhấn nút ✓ (Build) hoặc `Ctrl+Alt+B`
2. Nếu thành công, thấy dòng: **SUCCESS**

**Lỗi thường gặp:**
- `fatal error: config.h: No such file` → file chưa tạo hoặc sai thư mục
- `undefined reference` → thiếu file `.cpp` tương ứng

### Bước 6: Nạp firmware (Upload)

1. Nhấn nút → (mũi tên phải) trên status bar hoặc `Ctrl+Alt+U`
2. Nếu thành công, thấy:
   ```
   Writing at 0x00010000... (100%)
   Hard resetting via RTS pin...
   ```

> **Lưu ý**: Nếu báo lỗi "Failed to connect": giữ nút **BOOT** trên ESP32, nhấn Upload, thả nút BOOT khi thấy dòng "Connecting..."

### Bước 7: Mở Serial Monitor

Nhấn biểu tượng 🔌 trên status bar hoặc `Ctrl+Alt+M`. Đảm bảo baud rate = **115200**.

### Bước 8: Xác nhận firmware hoạt động

Nhấn nút **RST** (Reset) trên board ESP32. Sẽ thấy:

```
ARM INIT
ARM READY
```

- ✅ Thấy `ARM READY` → firmware đã nạp và chạy thành công!
- ❌ Thấy `ERR:PCA9685` → kiểm tra lại dây I2C (Bài 2)

### Bước 9: Nhận xét và kết luận

*(Sinh viên ghi nhận xét)*

## 🧩 Bài Tập Mở Rộng

1. Thử rút 1 dây SDA, nhấn Reset. Quan sát Serial Monitor có báo lỗi gì? Cắm lại và Reset để phục hồi.
2. Mở file `config.h`, tìm dòng `#define CFG_BAUD 115200`. Nếu đổi thành `9600`, bạn cần thay đổi gì ở Serial Monitor?

---

[⬅️ Bài 2: Kết nối phần cứng](../nhom-A-thiet-lap-phan-cung/bai-02-ket-noi-phan-cung.md) | [➡️ Bài 4: Điều khiển từng khớp](bai-04-dieu-khien-tung-khop.md)
