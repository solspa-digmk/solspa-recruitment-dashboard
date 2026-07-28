# Recruitment Dashboard — Phase 1 Implementation Plan
Dự án: Recruitment CRM Dashboard cho SOL SPA
Phiên bản: 1.0
Ngày: 2026-07-28

---

## 1. Mục tiêu Phase 1
- Tạo hệ thống quản lý ứng viên tập trung cho 9 chi nhánh.
- Pipeline tuyển dụng rõ ràng từ ghi nhận → hired.
- Dashboard xem được trên điện thoại/web.
- Không dùng Google Form; nhập tay/import/Trợ giúp Telegram.
- 0 quota/Codex; script-only sync.

## 2. Phạm vi
- Bao gồm 9 chi nhánh: Phòng khám Q7, LCP, LCR, RNS, Mercure VT, Minera Bình Châu, Lan Rừng, Hoàn Mỹ, Đà Lạt.
- Bao gồm 5 vị trí chính: Phó Giám Đốc, Quản lý/Phó Quản lý chi nhánh, Lễ tân, Bác sĩ/Y sĩ, Trị liệu viên.
- Không bao gồm xin phê duyệt/offer tự động; chỉ theo dõi.

## 3. Nguồn dữ liệu
- Google Sheet master.
- Không dùng Google Form.
- Có thể nhập: thủ công, import CV, nhận CV qua email/Telegram rồi đưa vào Sheet.

## 4. Cấu trúc Google Sheet — 6 tabs

### Tab 1: Candidates
Cột:
- candidate_id
- created_at
- updated_at
- full_name
- phone
- email
- zalo
- position_applied
- preferred_branch
- assigned_branch
- branch_flexibility
- region_preference
- source
- cv_link
- experience_years
- current_company
- expected_salary
- available_date
- english_level
- license_status
- stage
- status
- owner
- next_action
- next_follow_up_date
- interview_date
- interviewer
- screening_score
- interview_score
- trial_score
- final_score
- decision
- offer_salary
- onboard_date
- notes

### Tab 2: Branches
Cột:
- branch_id
- branch_name
- branch_type
- region
- address
- manager
- contact
- active
- notes

### Tab 3: Positions
Cột:
- position_id
- position_name
- level
- department
- default_pipeline
- priority
- notes

### Tab 4: Hiring_Demand
Cột:
- demand_id
- branch_id
- position_id
- open_headcount
- priority
- target_start_date
- status
- requested_by
- notes

### Tab 5: Interview_Checklists
Cột:
- position_id
- criterion
- weight
- score_1
- score_3
- score_5
- notes

### Tab 6: Activity_Log
Cột:
- activity_id
- candidate_id
- date
- action_type
- from_stage
- to_stage
- owner
- notes
- next_follow_up_date

### Tab 7: Dashboard_Config
Cột:
- config_type
- value
- label
- active
- sort_order

## 5. Pipeline chuẩn
- New → Screening → Branch Match → Contacted → Interview Scheduled → Interview 1 → Interview 2/Trial → Offer → Hired → Onboarded
- Các nhánh phụ: Rejected, Talent Pool, Blacklist.

## 6. Dashboard layout đề xuất
- KPI cards: tổng ứng viên, mới tuần này, đang phỏng vấn, offer pending, hired tháng này, tỷ lệ chuyển đổi, thời gian trung bình.
- Demand by Branch: bảng nhu cầu tuyển theo chi nhánh và vị trí.
- Branch Funnel: tỷ lệ từng stage theo chi nhánh.
- Candidate table: có filter theo vị trí, chi nhánh, nguồn, stage, owner, tháng, điểm.
- Kanban view: theo stage.
- Alert board: chi nhánh/vị trí có risk thiếu ứng viên.

## 7. Kế hoạch file/repo
- Repo: solspa-recruitment-dashboard
- Thư mục chính:
  - index.html
  - js/filters.js
  - css/style.css
  - data/candidates.json
  - data/branches.json
  - data/positions.json
  - data/demand.json
  - scripts/sync_sheet_to_json.py
  - docs/plan.md

## 8. Tiêu chí verify Phase 1
- Sheet có 6 tabs và dữ liệu mẫu đúng schema.
- Dashboard load được local JSON.
- Filter theo chi nhánh/vị trí/stage hoạt động.
- KPI cards tính đúng.
- Public URL trả về HTTP 200 nếu publish.
- Cron sync chạy không lỗi.

## 9. Công việc cần duyệt trước khi build
- Xác nhận schema đúng yêu cầu.
- Xác nhận danh sách chi nhánh và vị trí.
- Xác nhận pipeline stages.
- Xác nhận KPI cần ưu tiên.
- Xác nhận repo đích và nơi publish.

---
*Owner: Ms. Giang Vu*
*Maintained by: CEO AI / Hermes Agent*
