# Bài 6: Lập Trình Chuỗi Hoạt Động Tự Động

## 🎯 Mục tiêu

- Thiết kế chuỗi lệnh để robot thực hiện tác vụ gắp – di chuyển – thả vật thể
- Sử dụng thành thạo kết hợp lệnh A, M, S, W để tạo chuyển động có trình tự
- Gửi tuần tự nhiều lệnh qua Serial để robot thực hiện liên tục

## 📦 Chuẩn bị

- Robot đã kết nối và firmware hoạt động tốt
- Một vật thể nhỏ, nhẹ để thử gắp (cục tẩy, khối gỗ nhỏ, nắp bút)
- Đặt vật thể ở vị trí trước mặt robot, trong tầm với

## 📝 Các Bước Thực Hành

### Bước 1: Lập kế hoạch các giai đoạn

Tác vụ "gắp vật từ vị trí A, đặt sang vị trí B":

| Giai đoạn | Hành động | Mô tả |
|:---:|:---|:---|
| 1 | Chuẩn bị | Về Home, mở kẹp |
| 2 | Tiếp cận | Di chuyển đến phía trên vật thể |
| 3 | Hạ xuống | Hạ cánh tay xuống ngang vật thể |
| 4 | Gắp | Đóng kẹp |
| 5 | Nâng lên | Nâng cánh tay lên |
| 6 | Di chuyển | Xoay đế đến vị trí B |
| 7 | Hạ và thả | Hạ xuống, mở kẹp |
| 8 | Rút về | Nâng lên, về Home |

### Bước 2: Chuẩn bị (đặt tốc độ phù hợp)

```
S 0 3
S 1 2
S 2 2
S 3 3
S 4 3
S 5 5
H
W
→ Đợi DONE
```

### Bước 3: Mở kẹp và tiếp cận vật thể

```
M 5 60
W
A 90 120 130 90 90 60
W
→ Đợi DONE. Kẹp mở, tay ở phía trên vật thể.
```

> **Lưu ý**: Các góc dưới đây là giá trị mẫu. Cần điều chỉnh tùy vị trí thực tế.

### Bước 4: Hạ xuống và gắp

```
A 90 140 140 90 90 60
W
M 5 110
W
→ Kẹp đóng, gắp chặt vật thể.
```

### Bước 5: Nâng lên và di chuyển

```
A 90 100 90 90 90 110
W
M 0 45
W
→ Robot xoay đế sang vị trí B (góc 45°) trong khi giữ vật.
```

### Bước 6: Hạ xuống và thả

```
A 45 130 130 90 90 110
W
M 5 60
W
→ Kẹp mở, thả vật thể tại vị trí B.
```

### Bước 7: Rút về Home

```
A 45 100 90 90 90 90
W
H
W
→ Robot trở về vị trí ban đầu. Tác vụ hoàn thành!
```

### Bước 8: Nhận xét và kết luận

*(Sinh viên ghi nhận xét)*

## 🧩 Bài Tập Mở Rộng

1. Viết toàn bộ chuỗi lệnh vào file `.txt`, sao chép dán vào Serial Monitor để robot thực hiện tự động.
2. Thay đổi vị trí A và B, tự tìm các góc phù hợp bằng lệnh M.
3. Lập trình chuỗi hành động để robot xếp 2–3 vật thể chồng lên nhau.

---

[⬅️ Bài 5: Điều khiển đồng thời](../nhom-B-firmware-va-serial/bai-05-dieu-khien-dong-thoi.md) | [➡️ Bài 7: Python & GUI](bai-07-python-gui.md)
