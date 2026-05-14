# Bài 2: Kết Nối Phần Cứng ESP32 – PCA9685 – Robot Arm

## 🎯 Mục tiêu

- Nhận biết các chân kết nối I2C trên ESP32 và PCA9685
- Kết nối đúng 4 dây I2C giữa ESP32 và PCA9685
- Kết nối đúng 6 servo của robot vào đúng kênh trên PCA9685
- Cấp nguồn an toàn cho hệ thống

## 📦 Chuẩn bị

- Bộ Kit Robot 6DOF đã nhận biết ở Bài 1
- 4 dây nối Dupont cái-cái (đi kèm Kit hoặc mua riêng)
- Nguồn ngoài 5V–6V / 3A trở lên (adapter hoặc pin) để cấp riêng cho servo

> ⚠️ **CẢNH BÁO**: Tuyệt đối không dùng nguồn USB từ máy tính để cấp cho servo. Servo kéo dòng lớn (mỗi con 500mA–1A) sẽ gây hư hỏng cổng USB hoặc board ESP32.

## 📝 Các Bước Thực Hành

### Bước 1: Kết nối mạch I2C

Thực hiện đấu nối các linh kiện sử dụng 4 dây Dupont cái-cái:

| PCA9685 | ESP32 | Màu dây gợi ý | Chức năng |
|:---:|:---:|:---:|:---|
| SDA | GPIO 21 | 🟢 Xanh lá | Dữ liệu I2C |
| SCL | GPIO 22 | 🟡 Vàng | Xung nhịp I2C |
| GND | GND | ⚫ Đen | Mass chung |
| VCC | 3V3 | 🔴 Đỏ | Nguồn logic |

> ⚠️ **Lưu ý**: Kiểm tra kỹ từng dây trước khi cấp nguồn. Nối sai SDA/SCL chỉ khiến mạch không giao tiếp được, nhưng nối sai VCC hoặc GND có thể gây hư hỏng board mạch.

### Bước 2: Xác định kênh servo trên PCA9685

Module PCA9685 có 16 cổng servo (đánh số 0–15). Mỗi cổng gồm 3 pin: GND (ngoài cùng) – VCC (giữa) – PWM (trong cùng). Firmware sử dụng 6 kênh đầu tiên:

| Kênh PCA9685 | Khớp Robot | Servo |
|:---:|:---|:---|
| 0 | J0 – Base | Servo đế |
| 1 | J1 – Shoulder | Servo vai |
| 2 | J2 – Elbow | Servo khuỷu |
| 3 | J3 – Wrist Pitch | Servo cổ tay |
| 4 | J4 – Wrist Roll | Servo xoay |
| 5 | J5 – Gripper | Servo kẹp |

### Bước 3: Cắm servo vào PCA9685

Lần lượt cắm phích cắm 3 pin của từng servo vào đúng kênh trên PCA9685:

- Dây **nâu** (GND) → pin ngoài cùng (cạnh viền board)
- Dây **đỏ** (VCC) → pin giữa
- Dây **cam/vàng** (Signal/PWM) → pin trong cùng

> ⚠️ **Lưu ý**: Nếu cắm ngược (dây nâu vào pin Signal), servo không quay nhưng có thể bị hư nếu để lâu. Luôn kiểm tra chiều cắm: dây nâu hướng ra ngoài mép board.

### Bước 4: Kết nối nguồn servo riêng

Trên module PCA9685, có cổng domino xanh lá (screw terminal) đánh dấu **V+** và **GND**:

- Dây dương (+) → V+
- Dây âm (−) → GND

> **Lưu ý**: Hệ thống có 2 nguồn: USB từ máy tính cấp cho ESP32, nguồn ngoài 5V–6V cấp cho servo qua PCA9685. Hai nguồn chia sẻ chung dây GND.

### Bước 5: Kiểm tra tổng thể trước khi bật nguồn

Checklist:

- [ ] 4 dây I2C: SDA↔SDA, SCL↔SCL, GND↔GND, 3V3↔VCC
- [ ] 6 servo cắm đúng kênh 0–5, đúng chiều (nâu ra ngoài)
- [ ] Nguồn servo (5–6V) nối vào domino V+ và GND
- [ ] Cáp USB nối ESP32 với máy tính

### Bước 6: Nhận xét và kết luận

*(Sinh viên ghi nhận xét)*

## 🧩 Bài Tập Mở Rộng

1. I2C là gì? Tại sao chỉ cần 2 dây (SDA, SCL) mà có thể điều khiển 16 kênh servo?
2. Nếu muốn điều khiển thêm 1 cánh tay robot nữa (thêm 6 servo), bạn cần thay đổi gì trên phần cứng? *(Gợi ý: PCA9685 có jumper thay đổi địa chỉ I2C)*

---

[⬅️ Bài 1: Làm quen Kit](bai-01-lam-quen-kit.md) | [➡️ Bài 3: Nạp firmware](../nhom-B-firmware-va-serial/bai-03-nap-firmware.md)
