# Dự Án Game UNO Bằng Python (Pygame)

Chào mừng bạn đến với dự án Game UNO! Đây là một phiên bản trò chơi bài UNO kinh điển được xây dựng hoàn toàn bằng Python và thư viện đồ họa Pygame. Dự án áp dụng kiến trúc **MVC (Model - View - Controller)** kết hợp với Strategy Pattern dành cho Bot (AI) để đảm bảo mã nguồn gọn gàng, dễ bảo trì và dễ mở rộng.

## ✨ Các Tính Năng Nổi Bật

1. **Chế Độ Chơi Đa Dạng**:
   - **Đơn người chơi (Chơi với máy)**: Chọn mức độ thông minh của Bot (Dễ, Vừa, Khó).
   - **Đa người chơi**: Chơi cùng 3 hoặc 4 người (bao gồm người chơi thật và bot với các độ khó khác nhau).
   
2. **Luật Chơi Phong Phú**:
   - Chế độ 2 người: Hỗ trợ **Stacking Rule** (luật cộng dồn +2 và +4). Người chơi có thể đánh lá +2 đè lên +2 hoặc +4 đè lên +4 để đẩy hình phạt sang người kế tiếp.
   - Chế độ nhiều người (>2): Tắt chế độ cộng dồn, người bị phạt sẽ lập tức bốc bài và mất lượt.
   - Phạt bốc 2 lá nếu bạn quên hô "UNO!" trước khi đánh lá bài kế cuối.
   - Hệ thống tính điểm xếp hạng dựa trên luật Uno truyền thống ở cuối ván đấu.

3. **Trí Tuệ Nhân Tạo (Bot AI)**:
   - **Easy Bot**: Đánh bài ngẫu nhiên hợp lệ.
   - **Normal Bot**: Có chiến thuật nhẹ, biết cách để dành bài chức năng (Draw 4, Wild) khi thật sự cần.
   - **Hard Bot**: Có trí nhớ (ghi nhớ màu đã bị đánh, bài bị rút), tính toán để ép người chơi khác rút bài và chặn màu mà người tiếp theo không có.

## 📁 Cấu Trúc Thư Mục (Kiến trúc MVC)

- **`model/` (Logic & Data)**: Quản lý lá bài (`card.py`), bộ bài (`deck.py`), trạng thái người chơi (`player.py`) và cốt lõi vòng lặp của trò chơi (`game_logic.py`).
- **`view/` (Giao Diện UI/UX)**: Đảm nhận phần vẽ đồ họa lên màn hình với Pygame.
  - `DonNguoiChoi/`: Giao diện dành riêng cho chế độ 1 người chơi.
  - `DaNguoiChoi/`: Giao diện dành riêng cho chế độ bàn 3-4 người.
  - Hỗ trợ màn hình cài đặt, hiển thị font chữ, hiệu ứng âm thanh và nhạc nền.
- **`Controller/`**: Cầu nối trung gian. Nhận sự kiện click chuột/bàn phím từ người chơi, ra lệnh cho **Model** cập nhật logic và chỉ đạo **View** thay đổi giao diện.
- **`bots/`**: Nơi chứa riêng biệt thuật toán quyết định nước đi của AI (`easy_bot.py`, `normal_bot.py`, `hard_bot.py`).

## 🚀 Cách Cài Đặt và Chạy Game

### Yêu Cầu Hệ Thống
- Python 3.8 trở lên.
- Cần cài đặt thư viện `pygame` và `pgzero` (Pygame Zero) để hỗ trợ chạy môi trường game.

### Cài Đặt
Bạn mở Terminal (Command Prompt) tại thư mục game và chạy lệnh sau để cài đặt các thư viện cần thiết:
```bash
pip install pygame pgzero
```

### Khởi Chạy
Chạy file gốc để bắt đầu trò chơi:
```bash
python main.py
```
*(Nếu bạn sử dụng Windows, bạn cũng có thể click đúp vào file `run.bat` để chạy nhanh)*

## 📜 Luật Chơi (Tóm tắt)
- Mục tiêu: Trở thành người đầu tiên đánh hết bài trên tay.
- Các lá bài:
  - **Bài số (0-9)**: Đánh cùng màu hoặc cùng số với lá trên cùng.
  - **Skip (Bỏ lượt)**, **Reverse (Đảo chiều)**, **+2 (Rút 2 lá)**: Chỉ đánh cùng màu hoặc đánh lên trên lá bài cùng chức năng.
  - **Wild (Đổi màu)**, **Wild +4 (Đổi màu & Rút 4 lá)**: Đánh được bất cứ lúc nào, cho phép bạn chọn màu cho lượt tiếp theo.
- **Hô UNO**: Đừng quên bấm vào nút "UNO" khi bạn chỉ còn đúng 2 lá trên tay (tức là chuẩn bị đánh lá kế cuối)!

---
*Dự án UNO này là thành quả của sự tâm huyết giúp ứng dụng các kỹ thuật cấu trúc code chuyên nghiệp vào việc phát triển trò chơi với Python.*
