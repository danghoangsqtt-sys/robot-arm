# Bài 4: Điều Khiển Từng Khớp Servo

## 🎯 Mục tiêu

- Sử dụng lệnh **M** để di chuyển từng khớp servo đến góc mong muốn
- Sử dụng lệnh **G** để đọc góc hiện tại của mỗi khớp
- Sử dụng lệnh **T** để xem trạng thái toàn bộ 6 khớp
- Sử dụng lệnh **H** để đưa robot về vị trí Home
- Hiểu được giới hạn góc của từng khớp và tác dụng của việc clamp góc

## 📦 Chuẩn bị

- Nạp Firmware mẫu của bài thực hành 4 cho ESP32
- Nguồn servo đã cấp (adapter 5–6V)

> ⚠️ Đảm bảo cánh tay robot được đặt trên bàn vững chắc, không có vật cản xung quanh.

## 📋 Bảng Lệnh Tham Chiếu

| Lệnh | Cú pháp | Chức năng | Ví dụ |
|:---:|:---|:---|:---|
| **M** | `M <id> <góc>` | Di chuyển 1 khớp đến góc chỉ định | `M 0 45` |
| **G** | `G <id>` | Đọc góc hiện tại của 1 khớp | `G 0` → `VAL:0:90` |
| **T** | `T` | Xem trạng thái toàn bộ 6 khớp | `STA:90,70,90,90,90,90` |
| **H** | `H` hoặc `H <id>` | Đưa về Home (tất cả hoặc 1 khớp) | `H` hoặc `H 0` |
| **I** | `I` | Xem thông tin cấu hình | CFG cho mỗi khớp |

## 📝 Các Bước Thực Hành

### Phần A: Di chuyển khớp J0 (Base – Đế xoay)

**Bước 1**: Xem góc hiện tại
```
G 0
→ VAL:0:90   (khớp 0 đang ở góc 90°, vị trí Home)
```

**Bước 2**: Xoay đế sang phải (giảm góc)
```
M 0 45
→ OK   (Đế robot từ từ xoay sang phải đến góc 45°)
```

**Bước 3**: Xoay đế sang trái (tăng góc)
```
M 0 135
→ OK   (Đế xoay sang trái đến góc 135°)
```

**Bước 4**: Đưa khớp J0 về Home
```
H 0
→ OK   (Đế trở về vị trí 90°)
```

### Phần B: Điều khiển các khớp khác

**Bước 5**: Điều khiển khớp J1 (Shoulder – Vai)
```
M 1 100     → nâng vai lên
M 1 70      → hạ vai về min
```

> **Lưu ý**: Khớp J1 có giới hạn 70°–150°. Nếu gõ `M 1 30`, firmware sẽ tự động clamp về 70°.

**Bước 6**: Điều khiển khớp J5 (Gripper – Kẹp)
```
M 5 60      → mở kẹp hết cỡ
M 5 120     → đóng kẹp hết cỡ
M 5 90      → đóng kẹp vừa phải
```

### Phần C: Kiểm tra trạng thái

**Bước 7**: Kiểm tra trạng thái toàn bộ
```
T
→ STA:90,70,90,90,90,90
```

**Bước 8**: Xem thông tin cấu hình
```
I
→ (6 dòng CFG: góc min, max, Home, tốc độ hiện tại)
```

**Bước 9**: Đưa toàn bộ robot về Home
```
H
→ OK   (Toàn bộ 6 khớp về vị trí Home)
```

### Bước 10: Nhận xét và kết luận

*(Sinh viên ghi nhận xét)*

## 🧩 Bài Tập Mở Rộng

1. Ghi lại bảng: thử di chuyển lần lượt từng khớp J0–J5 đến góc min và max. Quan sát và mô tả chuyển động thực tế.
2. Thử gõ lệnh sai, ví dụ: `M 9 90` (id không tồn tại), `M` (thiếu tham số). Quan sát phản hồi ERR từ firmware.

---

[⬅️ Bài 3: Nạp firmware](bai-03-nap-firmware.md) | [➡️ Bài 5: Điều khiển đồng thời](bai-05-dieu-khien-dong-thoi.md)
