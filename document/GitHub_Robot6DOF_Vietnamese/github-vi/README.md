<div align="center">

# 🤖 Tài Liệu Thực Hành Cánh Tay Robot 6DOF

### ESP32 + PCA9685 + Robot Arm 6DOF Lab Manual

[![ESP32](https://img.shields.io/badge/MCU-ESP32-blue?style=for-the-badge&logo=espressif)](https://www.espressif.com/)
[![PlatformIO](https://img.shields.io/badge/IDE-PlatformIO-orange?style=for-the-badge&logo=platformio)](https://platformio.org/)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)
[![Language](https://img.shields.io/badge/Lang-Vietnamese-red?style=for-the-badge)](.)

*Hệ thống bài thực hành điều khiển cánh tay Robot 6 bậc tự do sử dụng ESP32, PCA9685 và Arduino Framework*

[English Version](../github-en/README.md)

</div>

---

## 📋 Tổng Quan

Tài liệu này cung cấp **9 bài thực hành** có tính kế thừa, từ cơ bản đến nâng cao, giúp sinh viên nắm vững kiến thức lập trình nhúng, IoT và điều khiển robot thông qua bộ Kit phần cứng thực tế.

### 🎯 Đối Tượng

- Sinh viên các ngành Kỹ thuật Điện tử, CNTT, Tự động hóa
- Giảng viên tổ chức thực hành các môn: Kỹ thuật Vi xử lý, Lập trình Nhúng, IoT

### 🔧 Phần Cứng Sử Dụng

| Thành phần | Mô tả |
|:---|:---|
| **ESP32 DevKit V1** | Vi điều khiển 32-bit, WiFi/Bluetooth tích hợp |
| **Module PCA9685** | IC điều khiển PWM 16 kênh, giao tiếp I²C |
| **Cánh tay Robot 6DOF** | 6 khớp xoay (J0–J5), dẫn động bằng servo |
| **Nguồn ngoài** | Adapter 5V–6V / 3A trở lên cho servo |

---

## 📂 Cấu Trúc Tài Liệu

```
📦 robot-arm-lab/
├── 📖 README.md                          ← Bạn đang ở đây
├── 📁 phan-1-gioi-thieu/
│   └── README.md                         ← Giới thiệu Kit & phần mềm
├── 📁 nhom-A-thiet-lap-phan-cung/
│   ├── bai-01-lam-quen-kit.md            ← Bài 1: Làm quen Kit & cài đặt
│   └── bai-02-ket-noi-phan-cung.md       ← Bài 2: Kết nối ESP32-PCA9685-Robot
├── 📁 nhom-B-firmware-va-serial/
│   ├── bai-03-nap-firmware.md             ← Bài 3: Nạp firmware & Serial Monitor
│   ├── bai-04-dieu-khien-tung-khop.md     ← Bài 4: Điều khiển từng khớp servo
│   └── bai-05-dieu-khien-dong-thoi.md     ← Bài 5: Điều khiển đồng thời & tốc độ
├── 📁 nhom-C-ung-dung-nang-cao/
│   ├── bai-06-chuoi-tu-dong.md            ← Bài 6: Lập trình chuỗi tự động
│   ├── bai-07-python-gui.md               ← Bài 7: Điều khiển bằng Python & GUI
│   ├── bai-08-webserver-esp32.md          ← Bài 8: Điều khiển qua Web Server
│   └── bai-09-bluetooth-esp32.md          ← Bài 9: Điều khiển qua Bluetooth
└── 📁 firmware/
    └── README.md                          ← Hướng dẫn firmware
```

---

## 🗺️ Lộ Trình Học Tập

```
┌─────────────────────────────────────────────────────────────────┐
│  NHÓM A: THIẾT LẬP PHẦN CỨNG                                   │
│  ┌──────────┐    ┌──────────────────┐                           │
│  │  Bài 1   │───▶│     Bài 2        │                           │
│  │ Làm quen │    │ Kết nối phần cứng│                           │
│  └──────────┘    └────────┬─────────┘                           │
├───────────────────────────┼─────────────────────────────────────┤
│  NHÓM B: FIRMWARE & SERIAL│                                     │
│               ┌───────────▼──────────┐                          │
│               │      Bài 3           │                          │
│               │  Nạp firmware        │                          │
│               └───────────┬──────────┘                          │
│          ┌────────────────┼────────────────┐                    │
│  ┌───────▼──────┐   ┌────▼─────────┐                           │
│  │    Bài 4     │   │    Bài 5     │                            │
│  │  Từng khớp   │   │  Đồng thời   │                            │
│  └───────┬──────┘   └────┬─────────┘                           │
├──────────┼───────────────┼──────────────────────────────────────┤
│  NHÓM C: ỨNG DỤNG NÂNG CAO                                     │
│  ┌───────▼───────────────▼──────────┐                           │
│  │         Bài 6: Chuỗi tự động     │                           │
│  └───────────────┬──────────────────┘                           │
│     ┌────────────┼────────────┬─────────────┐                   │
│  ┌──▼───┐    ┌───▼──┐    ┌───▼──┐                               │
│  │Bài 7 │    │Bài 8 │    │Bài 9 │                               │
│  │Python │    │ Web  │    │  BT  │                               │
│  └──────┘    └──────┘    └──────┘                               │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📊 Bảng Mô Tả 6 Khớp Robot

| Khớp | Tên | Chức năng | Góc Min | Góc Max | Góc Home |
|:---:|:---|:---|:---:|:---:|:---:|
| J0 | Base (Đế) | Xoay toàn bộ cánh tay | 0° | 180° | 90° |
| J1 | Shoulder (Vai) | Nâng/hạ cánh tay trên | 70° | 150° | 70° |
| J2 | Elbow (Khuỷu) | Gập/duỗi cánh tay dưới | 0° | 150° | 90° |
| J3 | Wrist Pitch (Cổ tay) | Ngửa/úp bàn kẹp | 0° | 180° | 90° |
| J4 | Wrist Roll (Xoay) | Xoay bàn kẹp | 0° | 180° | 90° |
| J5 | Gripper (Kẹp) | Mở/đóng kẹp | 60° | 120° | 90° |

---

## ⚡ Bắt Đầu Nhanh

```bash
# 1. Clone repository
git clone https://github.com/YOUR_USERNAME/robot-arm-lab.git

# 2. Cài đặt VS Code + PlatformIO
# Xem chi tiết tại: phan-1-gioi-thieu/README.md

# 3. Bắt đầu từ Bài 1
# Mở file: nhom-A-thiet-lap-phan-cung/bai-01-lam-quen-kit.md
```

---

## 🤝 Đóng Góp

Mọi đóng góp đều được hoan nghênh! Vui lòng tạo **Issue** hoặc **Pull Request**.

## 📄 Giấy Phép

Dự án được phân phối theo giấy phép [MIT](LICENSE).

---

<div align="center">

**Được phát triển bởi Hoang** | *Dành cho sinh viên kỹ thuật Việt Nam*

</div>
