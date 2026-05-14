# Bài 5: Điều Khiển Đồng Thời Nhiều Khớp và Tốc Độ

## 🎯 Mục tiêu

- Sử dụng lệnh **A** để di chuyển đồng thời 6 khớp đến các góc chỉ định
- Sử dụng lệnh **S** để thay đổi tốc độ di chuyển của từng khớp
- Sử dụng lệnh **W** để đợi robot hoàn thành chuyển động
- Sử dụng lệnh **X** để dừng khẩn cấp

## 📦 Chuẩn bị

- Nạp Firmware mẫu của bài thực hành 5 vào ESP32
- Nguồn servo đã cấp (adapter 5–6V)

## 📋 Bảng Lệnh Mới

| Lệnh | Cú pháp | Chức năng |
|:---:|:---|:---|
| **A** | `A <a0> <a1> <a2> <a3> <a4> <a5>` | Di chuyển đồng thời 6 khớp |
| **S** | `S <id> <tốc_độ>` | Đặt tốc độ cho 1 khớp (°/tick) |
| **W** | `W` | Đợi tất cả khớp hoàn thành → trả về `DONE` |
| **X** | `X` | Dừng khẩn cấp tất cả khớp |

### Kiến thức nền

- **Di chuyển đồng thời (A)**: Gán góc đích cho 6 khớp cùng lúc, tạo chuyển động phối hợp mượt mà.
- **Thay đổi tốc độ (S)**: Tốc độ = bước nhảy mỗi tick 20ms. Mặc định = 1°/tick. Tăng lên 10 = nhanh gấp 10 lần.
- **Đồng bộ (W)**: Firmware chỉ trả về `DONE` khi tất cả khớp đã dừng ở đích.
- **Dừng khẩn cấp (X)**: Ép góc đích = góc hiện tại → servo ngừng ngay, không giật.

## 📝 Các Bước Thực Hành

### Bước 1: Đưa robot về Home
```
H
```

### Bước 2: Di chuyển tất cả khớp cùng lúc
```
A 45 100 120 45 135 60
→ OK
```
Cả 6 khớp đồng thời di chuyển: J0=45°, J1=100°, J2=120°, J3=45°, J4=135°, J5=60°.

### Bước 3: Kiểm tra trạng thái
```
T
→ So sánh kết quả với các góc đã gửi
```

### Bước 4: Tăng tốc khớp J0
```
S 0 10
M 0 180
→ J0 di chuyển nhanh hơn nhiều (10°/tick thay vì 1°/tick)
```

### Bước 5: So sánh tốc độ khác nhau
```
H
S 0 1
S 2 15
A 0 100 150 90 90 90
→ Quan sát: J2 đến đích trước J0 vì tốc độ nhanh hơn
```

### Bước 6: Sử dụng lệnh W (Wait)
```
S 0 1
M 0 180
W
→ (chưa trả lời ngay... đợi robot xong) → DONE
```

### Bước 7: Sử dụng lệnh X (Dừng khẩn cấp)
```
H
(đợi xong)
S 0 1
M 0 0
(trong khi đang chuyển động, gõ nhanh:)
X
→ OK   (Robot dừng ngay tại vị trí hiện tại)
T
→ (xem góc dừng)
```

### Bước 8: Nhận xét và kết luận

*(Sinh viên ghi nhận xét)*

## 🧩 Bài Tập Mở Rộng

1. Viết toàn bộ chuỗi lệnh vào file `.txt`, mỗi dòng 1 lệnh. Sao chép và dán nhanh vào Serial Monitor để robot thực hiện tự động liên tục.
2. Thay đổi vị trí A và B, tự tìm các góc phù hợp bằng lệnh M thử từng khớp.
3. Lập trình chuỗi hành động để robot xếp 2–3 vật thể chồng lên nhau.

---

[⬅️ Bài 4: Điều khiển từng khớp](bai-04-dieu-khien-tung-khop.md) | [➡️ Bài 6: Chuỗi tự động](../nhom-C-ung-dung-nang-cao/bai-06-chuoi-tu-dong.md)
