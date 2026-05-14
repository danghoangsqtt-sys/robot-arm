# Phần 1: Giới Thiệu Kit Thực Hành và Phần Mềm Lập Trình

## 1.1. Giới thiệu

Tài liệu này hướng dẫn thực hành sử dụng bộ Kit IoT điều khiển cánh tay Robot 6 bậc tự do (6DOF). Các bài thực hành được thiết kế để sinh viên ứng dụng kiến thức lý thuyết đã học vào việc lập trình và điều khiển động cơ servo thực tế.

### Bộ Kit gồm 3 thành phần chính

- **Board ESP32 DevKit V1**: Vi điều khiển 32-bit tích hợp WiFi/Bluetooth, đóng vai trò bộ não xử lý trung tâm. Sinh viên vận dụng kiến thức môn Kỹ thuật vi xử lý (kiến trúc vi điều khiển, GPIO, I2C, UART) để lập trình điều khiển robot.
- **Module PCA9685**: IC điều khiển PWM 16 kênh qua giao tiếp I2C, cho phép điều khiển chính xác nhiều servo cùng lúc.
- **Cánh tay Robot 6DOF**: Cơ cấu cơ khí gồm 6 khớp xoay (J0–J5) được dẫn động bởi 6 servo, cho phép cánh tay di chuyển linh hoạt trong không gian.

## 1.2. Mục tiêu chung

### Về kiến thức
- Kiểm chứng trực tiếp kiến thức Điện tử số: quan sát tín hiệu PWM điều khiển servo, giao tiếp I2C giữa vi điều khiển và IC ngoại vi.
- Củng cố kiến thức Kỹ thuật vi xử lý: kiến trúc ESP32, cấu hình GPIO, giao tiếp UART/I2C, quy trình nạp firmware.
- Hiểu mô hình Lập trình nhúng IoT: luồng dữ liệu từ lệnh người dùng → vi điều khiển → bus I2C → PWM → cơ cấu cơ khí robot.

### Về kỹ năng
- Kết nối đúng phần cứng: bus I2C, nguồn servo, mapping kênh PWM cho từng khớp robot.
- Biên dịch, nạp firmware nhúng và giao tiếp Serial UART với vi điều khiển.
- Lập trình điều khiển từng khớp, đồng thời nhiều khớp, và chuỗi hành động tự động cho robot.
- Xây dựng ứng dụng điều khiển robot bằng Python (script tự động + giao diện GUI).

### Ứng dụng thực tiễn
- Lập trình và điều khiển cánh tay robot thực hiện các tác vụ: gắp, di chuyển, thả vật thể theo yêu cầu.
- Áp dụng quy trình phát triển nhúng (viết mã → biên dịch → nạp → debug) cho các dự án vi điều khiển khác.
- Thiết kế hệ thống IoT cơ bản: điều khiển thiết bị qua Serial, mở rộng sang WiFi/Bluetooth.

## 1.3. Yêu cầu tiên quyết

- **Kiến thức**: Sinh viên đã học lý thuyết các môn Điện tử số (tín hiệu số, PWM, giao thức I2C), Kỹ thuật vi xử lý (kiến trúc VĐK, GPIO, UART), và Lập trình nhúng IoT (mô hình IoT, lập trình C/C++ cơ bản).
- **Thiết bị**: Máy tính (Windows/macOS/Linux) với cổng USB.

## 1.4. Bảng mô tả 6 khớp Robot

| Khớp | Tên | Chức năng | Góc Min | Góc Max | Góc Home |
|:---:|:---|:---|:---:|:---:|:---:|
| J0 | Base (Đế) | Xoay toàn bộ cánh tay | 0° | 180° | 90° |
| J1 | Shoulder (Vai) | Nâng/hạ cánh tay trên | 70° | 150° | 70° |
| J2 | Elbow (Khuỷu) | Gập/duỗi cánh tay dưới | 0° | 150° | 90° |
| J3 | Wrist Pitch (Cổ tay) | Ngửa/úp bàn kẹp | 0° | 180° | 90° |
| J4 | Wrist Roll (Xoay) | Xoay bàn kẹp | 0° | 180° | 90° |
| J5 | Gripper (Kẹp) | Mở/đóng kẹp | 60° | 120° | 90° |

---

[⬅️ Quay lại Trang chính](../README.md) | [➡️ Nhóm A: Thiết lập phần cứng](../nhom-A-thiet-lap-phan-cung/bai-01-lam-quen-kit.md)
