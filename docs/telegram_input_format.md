# Telegram Input Format for Recruitment Dashboard

## Cấu trúc chuẩn khi nhập liệu ứng viên từ Telegram:
Tab đích trên Google Sheet: `Candidate_Telegram_Input`
Thứ tự cột chuẩn (10 cột):
1. `ID` (Để trống nếu tự sinh)
2. `Ho_ten` (Họ và tên ứng viên)
3. `SDT` (Số điện thoại)
4. `Email` (Địa chỉ email)
5. `Vi_tri` (Mã vị trí: `PGD`, `QLCN`, `PG`, `LT`, `BS`, `TLV`)
6. `Chi_nhanh` (Mã chi nhánh: `Q7`, `LCP`, `LCR`, `RNS`, `MVT`, `MBC`, `LR`, `HM`, `DL`)
7. `Nguon` (Nguồn ứng viên: `HotelJob`, `Trang tuyển dụng`, `LinkedIn`, `Email`, `Giới thiệu`, `Trực tiếp`, `Khác`)
8. `Stage` (Trạng thái phễu: `Mới`, `Sàng lọc`, `Phân chi nhánh`, `Đã liên hệ`, `Đã hẹn`, `PV1`, `PV2`, `Thử việc`, `Từ chối`, `Đã nhận việc`, `Nhóm tiềm năng`, `Danh sách đen`)
9. `Owner` (Người phụ trách)
10. `Next_action` (Hành động tiếp theo)
