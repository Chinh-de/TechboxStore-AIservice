# Hướng Dẫn Khắc Phục Sự Cố Cơ Bản (Troubleshoot) - Techbox Support

Tài liệu này được biên soạn bởi đội ngũ kỹ thuật Techbox Store, nhằm giúp Quý khách hàng tự chẩn đoán và xử lý các vấn đề thường gặp trên thiết bị di động/laptop tại nhà một cách nhanh chóng và an toàn.

---

## 1. Vấn Đề Về Pin & Sạc (Battery & Charging)

### 1.1. Máy sạc không vào điện hoặc sạc chập chờn
*   **Triệu chứng:** Cắm sạc nhưng không hiện biểu tượng tia sét, hoặc lúc nhận lúc không.
*   **Nguyên nhân & Khắc phục:**
    1.  **Kiểm tra phụ kiện (80% nguyên nhân):** Thử đổi một bộ cáp và củ sạc khác (chính hãng) đang hoạt động tốt. Cáp sạc bị đứt ngầm hoặc chân tiếp xúc bị mòn là nguyên nhân phổ biến nhất.
    2.  **Vệ sinh cổng sạc:** Dùng đèn pin soi vào cổng sạc. Nếu thấy bụi vải, xơ vải tích tụ, hãy dùng tăm nhựa hoặc bàn chải đánh răng khô nhẹ nhàng khều bụi ra. *Tuyệt đối không dùng vật kim loại cứng chọc vào làm gãy chân sạc.*
    3.  **Lỗi phần mềm:** Đôi khi hệ điều hành bị treo tiến trình sạc. Hãy thử **Khởi động lại máy (Restart)**.
    4.  **Nhiệt độ:** Nếu máy đang quá nóng (do chơi game, đi nắng), cơ chế bảo vệ sẽ ngắt sạc. Hãy để máy nguội bớt rồi sạc lại.

### 1.2. Pin tụt nhanh, máy nóng bất thường
*   **Khắc phục:**
    1.  **Kiểm tra ứng dụng ngốn pin:**
        *   *iOS:* Cài đặt -> Pin -> Xem danh sách ứng dụng dùng pin 24h qua.
        *   *Android:* Cài đặt -> Chăm sóc thiết bị -> Pin.
        *   -> Gỡ bỏ hoặc hạn chế quyền chạy nền của các ứng dụng lạ, ít dùng (Facebook, TikTok thường ngốn pin nhất).
    2.  **Tắt các kết nối dư thừa:** Tắt 4G/5G, Bluetooth, GPS (Vị trí) khi không cần thiết.
    3.  **Cập nhật phần mềm:** Nâng cấp lên phiên bản iOS/Android mới nhất để nhận các bản vá lỗi hiệu năng.
    4.  **Kiểm tra độ chai pin:**
        *   *iPhone:* Cài đặt -> Pin -> Tình trạng pin & Sạc. Nếu Dung lượng tối đa < 80% -> Cần thay pin.
        *   *Android:* Dùng app AccuBattery hoặc mang ra tiệm kiểm tra.

---

## 2. Vấn Đề Về Màn Hình & Cảm Ứng

### 2.1. Màn hình bị đơ, treo, không vuốt được
*   **Khắc phục (Hard Reset - Khởi động nóng):**
    *   **iPhone (Có FaceID - iPhone X trở lên):** Nhấn thả nhanh Tăng âm lượng -> Nhấn thả nhanh Giảm âm lượng -> Nhấn giữ nút Nguồn (Side button) khoảng 10s cho đến khi hiện logo Táo thì thả ra.
    *   **iPhone (Có nút Home):** Giữ Nguồn + Home khoảng 10s.
    *   **Samsung/Android:** Nhấn giữ đồng thời Nguồn + Giảm âm lượng khoảng 7-10s cho đến khi máy tắt và rung nhẹ khởi động lại.

### 2.2. Màn hình bị loạn cảm ứng (Ghost touch)
*   **Nguyên nhân:** Do miếng dán màn hình, do tay ướt, hoặc do cáp sạc kém chất lượng gây nhiễu điện.
*   **Khắc phục:**
    1.  Tháo bỏ miếng dán cường lực cũ.
    2.  Lau sạch màn hình và tay.
    3.  Thử đổi bộ sạc chính hãng khác.
    4.  Nếu vẫn bị -> Lỗi phần cứng màn hình (Cần thay thế).

---

## 3. Vấn Đề Về Kết Nối (Wifi, Bluetooth, 4G)

### 3.1. Wifi kết nối nhưng không có mạng hoặc chập chờn
*   **Khắc phục:**
    1.  **Quên mạng (Forget Network):** Vào Cài đặt -> Wifi -> Chọn chữ (i) hoặc mũi tên bên cạnh tên Wifi -> Chọn "Quên mạng này" -> Kết nối và nhập lại mật khẩu.
    2.  **Gia hạn thuê bao DHCP:** Trong cài đặt Wifi, chọn "Gia hạn hợp đồng thuê bao" (Renew Lease).
    3.  **Đặt lại cài đặt mạng (Reset Network Settings):**
        *   *iOS:* Cài đặt -> Cài đặt chung -> Chuyển hoặc đặt lại iPhone -> Đặt lại -> **Đặt lại cài đặt mạng** (Lưu ý: Sẽ mất hết pass Wifi đã lưu).
        *   *Android:* Cài đặt -> Hệ thống -> Tùy chọn đặt lại -> Đặt lại Wifi, di động và Bluetooth.
    4.  **Đổi DNS:** Chuyển DNS sang Google (8.8.8.8 / 8.8.4.4) hoặc Cloudflare (1.1.1.1).

### 3.2. Bluetooth không tìm thấy thiết bị / Tai nghe chỉ nghe 1 bên
*   **Khắc phục:**
    1.  Tắt Bluetooth và bật lại.
    2.  "Quên" thiết bị cũ và kết nối lại từ đầu.
    3.  Với tai nghe True Wireless (AirPods...): Bỏ 2 tai vào hộp, nhấn giữ nút Reset trên hộp khoảng 10s để reset tai nghe, sau đó kết nối lại.

---

## 4. Vấn Đề Về Âm Thanh (Loa, Mic)

### 4.1. Loa nghe nhỏ, rè
*   **Nguyên nhân:** Bụi bẩn bám dày đặc màng loa, hoặc màng loa bị rách, vào nước.
*   **Khắc phục:**
    1.  Dùng bàn chải đánh răng lông mềm, khô chải nhẹ nhàng màng loa để đẩy bụi ra.
    2.  Dùng băng dính (băng keo) dính nhẹ lên màng loa để lấy bụi.
    3.  Nếu loa bị rè (âm thanh vỡ) -> Thường là hỏng phần cứng, cần thay loa.

### 4.2. Gọi điện người bên kia không nghe (Lỗi Mic)
*   **Test Mic:** Mở ứng dụng Ghi âm (Voice Memos) và ghi âm thử một đoạn.
    *   *Nếu nghe lại thấy tiếng bình thường:* Mic phần cứng tốt. Lỗi do sóng yếu, hoặc xung đột phần mềm (Zalo/Messenger chưa cấp quyền Mic). Hãy kiểm tra lại quyền truy cập Micro trong Cài đặt -> Quyền riêng tư.
    *   *Nếu nghe lại không có tiếng hoặc tiếng xì xào:* Mic phần cứng bị hỏng hoặc bị bụi bít kín.

---

## 5. Các Mã Lỗi Thường Gặp (Error Codes)

### iPhone (Khi Restore/Update qua iTunes/3uTools)
*   **Lỗi 4013, 4014:** Thường do cáp kết nối lỏng hoặc lỗi phần cứng (Ổ cứng/NAND). -> Thử đổi cáp zin, đổi cổng USB.
*   **Lỗi -1, 1:** Lỗi Baseband (Mất IMEI/Sóng). -> Lỗi phần cứng nghiêm trọng trên Main.
*   **Lỗi 9:** Mất kết nối giữa chừng. -> Kiểm tra cáp và pin.

---

## 6. Khi Nào Cần Mang Máy Đến Techbox Store?

Nếu bạn đã thử các cách trên mà vẫn không khắc phục được, hoặc gặp các dấu hiệu nguy hiểm sau, hãy mang máy đến ngay Techbox Store:

1.  **Máy bị vào nước:** Cần tắt nguồn ngay, không được sạc, mang đi sấy khô chuyên dụng càng sớm càng tốt (trong 24h vàng).
2.  **Pin bị phồng:** Màn hình bị kênh lên, vỏ máy bị bung. Nguy cơ cháy nổ cao -> Cần thay pin gấp.
3.  **Treo Logo (Bootloop):** Máy cứ hiện logo rồi tắt, lặp lại liên tục.
4.  **Mất FaceID / TouchID:** Thường do đứt cáp hoặc lỗi main.
5.  **Màn hình chảy mực, sọc:** Lỗi hiển thị không thể sửa bằng phần mềm.

**Kênh Hỗ Trợ Kỹ Thuật Từ Xa (Miễn Phí):**
*   **Hotline:** 0905.555.666 (8:30 - 21:00)
*   **Zalo:** Techbox Technical Support
*   **Group Facebook:** Cộng đồng Techbox Support

*Chúng tôi luôn sẵn sàng lắng nghe và hỗ trợ bạn!*
