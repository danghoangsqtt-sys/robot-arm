# Bài 1: Làm Quen Với Kit và Cài Đặt Môi Trường

## 🎯 Mục tiêu

- Nhận biết và gọi tên đúng 3 thành phần chính của bộ Kit IoT Robot
- Cài đặt thành công phần mềm VS Code và PlatformIO
- Cài đặt thành công driver CP2102/CH340 cho ESP32
- Xác nhận ESP32 được nhận diện trên máy tính (COM port)

## 📦 Chuẩn bị

- Máy tính có kết nối Internet
- Cáp Micro-USB (đi kèm trong bộ Kit)
- Bộ Kit Robot 6DOF (chưa cần lắp ráp)

## 📝 Các Bước Thực Hành

### Bước 1: Mở hộp và kiểm tra bộ Kit

Lấy tất cả các thành phần ra khỏi hộp. Đặt lên bàn sạch, khô ráo. Kiểm tra đủ 3 thành phần chính:

- **Board ESP32 DevKit V1**: Board màu đen, có chip kim loại vuông ở giữa (module WiFi/BT), cổng Micro-USB ở cạnh, 2 hàng chân cắm hai bên.
- **Module PCA9685**: Board màu xanh dương, có hàng chân kết nối servo (3 pin: nâu-đỏ-vàng) dọc theo cạnh dài, đầu vào I2C (4 pin) ở cạnh ngắn, cổng nguồn servo riêng.
- **Cánh tay Robot 6DOF**: Khung nhôm/nhựa đen với 6 động cơ servo gắn tại các khớp, có dây nối 3 sợi (nâu-đỏ-cam) từ mỗi servo.

### Bước 2: Tải và cài đặt Visual Studio Code

1. Mở trình duyệt web, truy cập: https://code.visualstudio.com
2. Nhấn nút "Download" phù hợp với hệ điều hành (Windows/macOS/Linux)
3. Chạy file cài đặt, nhấn "Next" cho đến khi hoàn tất. Đánh dấu tùy chọn "Add to PATH" nếu có.

### Bước 3: Cài đặt PlatformIO Extension

1. Mở VS Code đã cài đặt
2. Nhấn `Ctrl+Shift+X` để mở Extensions
3. Trong ô tìm kiếm, gõ: `PlatformIO IDE`
4. Nhấn "Install" bên cạnh kết quả "PlatformIO IDE"
5. Đợi cài đặt hoàn tất (2–5 phút). VS Code sẽ yêu cầu "Reload"

> **Lưu ý**: Sau khi reload, biểu tượng PlatformIO (hình con kiến) sẽ xuất hiện ở thanh bên trái. Nếu thấy biểu tượng này, cài đặt thành công.

### Bước 4: Cài đặt Driver USB cho ESP32

Board ESP32 DevKit V1 sử dụng chip chuyển đổi USB-to-UART (thường là CP2102 hoặc CH340):

- **Với chip CP2102**: Tải driver tại https://www.silabs.com/developers/usb-to-uart-bridge-vcp-drivers
- **Với chip CH340**: Tải driver tại https://sparks.gogo.co.nz/ch340.html

> **Lưu ý**: Nếu không biết board dùng chip nào, hãy thử cài cả hai driver. Không gây xung đột.

### Bước 5: Kết nối ESP32 với máy tính

1. Dùng cáp Micro-USB cắm vào cổng USB trên board ESP32
2. Cắm đầu còn lại vào cổng USB của máy tính
3. Đèn LED đỏ trên board ESP32 sẽ sáng (báo có nguồn)

### Bước 6: Xác nhận COM port

| Hệ điều hành | Cách kiểm tra |
|:---|:---|
| **Windows** | Chuột phải Start → Device Manager → Ports (COM & LPT) → tìm "Silicon Labs CP210x" hoặc "CH340" |
| **macOS** | Terminal: `ls /dev/cu.*` → tìm dòng chứa "usbserial" |
| **Linux** | Terminal: `ls /dev/ttyUSB*` → thấy `/dev/ttyUSB0` hoặc tương tự |

> **Lưu ý**: Nếu không thấy COM port, thử đổi cáp USB (một số cáp chỉ sạc, không truyền dữ liệu) hoặc cài lại driver.

📝 **Ghi lại số COM port**: ____________

### Bước 7: Nhận xét và kết luận

*(Sinh viên ghi nhận xét)*

## 🧩 Bài Tập Mở Rộng

1. Tìm hiểu trên board ESP32 có bao nhiêu chân GPIO? Chân GPIO 21 và GPIO 22 dùng cho giao tiếp gì?
2. Quan sát module PCA9685, đếm xem có bao nhiêu cổng servo (3 pin)? Tại sao cần module này thay vì nối servo trực tiếp vào ESP32?

---

[⬅️ Phần 1: Giới thiệu](../phan-1-gioi-thieu/README.md) | [➡️ Bài 2: Kết nối phần cứng](bai-02-ket-noi-phan-cung.md)
