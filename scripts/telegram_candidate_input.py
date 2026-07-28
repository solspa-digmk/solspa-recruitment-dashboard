#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Telegram candidate input parser for SOL SPA Recruitment Dashboard.

Supports 2 formats:
1. Multi-field:
   /them_ung_vien
   Ho ten: Nguyen Van A
   SDT: 0901234567
   Email: a.nguyen@email.com
   Vi tri: LT
   Chi nhanh: LCP
   Nguon: TopCV
   Stage: Moi
   Owner: HR LCP
   Next action: Goi dien

2. CSV short:
   /add C011,Nguyen Van A,0901234567,a.nguyen@email.com,LT,LCP,TopCV,Mới,HR LCP,Gọi điện
"""

import json, re, sys
from pathlib import Path
from datetime import date

ROOT = Path('/Users/giangvu/.hermes/repos/solspa-recruitment-dashboard')
DATA = ROOT / 'data'
CANDIDATES_FILE = DATA / 'candidates.json'

POSITIONS = {
    'PGD': 'Phó Giám Đốc',
    'QLCN': 'Quản lý/Phó Quản lý chi nhánh',
    'LT': 'Lễ tân',
    'BS': 'Bác sĩ/Y sĩ',
    'TLV': 'Trị liệu viên',
}

BRANCHES = {
    'Q7': 'Phòng khám Q7',
    'LCP': 'LCP',
    'LCR': 'LCR',
    'RNS': 'RNS',
    'MVT': 'Mercure VT',
    'MBC': 'Minera Bình Châu',
    'LR': 'Lan Rừng',
    'HM': 'Hoàn Mỹ',
    'DL': 'Đà Lạt',
}

STAGES = [
    'Mới', 'Sàng lọc', 'Phân chi nhánh', 'Đã liên hệ', 'Đã hẹn',
    'PV1', 'PV2', 'Thử việc', 'Từ chối', 'Đã nhận việc',
    'Nhóm tiềm năng', 'Danh sách đen'
]

SOURCE_LABELS = ['Giới thiệu', 'Trang tuyển dụng', 'LinkedIn', 'Email', 'Trực tiếp', 'Khác']


def normalize_position(v: str) -> str:
    v = v.strip().upper()
    mapping = {'QUẢN LÝ/PHÓ QUẢN LÝ CHI NHÁNH': 'QLCN', 'BÁC SĨ/Y SĨ': 'BS', 'TRỊ LIỆU VIÊN': 'TLV', 'LỄ TÂN': 'LT', 'PHÓ GIÁM ĐỐC': 'PGD'}
    return mapping.get(v, v)


def normalize_branch(v: str) -> str:
    v = v.strip().upper()
    mapping = {'PHÒNG KHÁM Q7': 'Q7', 'MERCURE VT': 'MVT', 'MINERA BÌNH CHÂU': 'MBC', 'LAN RỪNG': 'LR', 'HOÀN MỸ': 'HM', 'ĐÀ LẠT': 'DL'}
    return mapping.get(v, v)


def normalize_stage(v: str) -> str:
    v = v.strip()
    aliases = {
        'MỚI': 'Mới', 'MOI': 'Mới',
        'SÀNG LỌC': 'Sàng lọc', 'SANG LOC': 'Sàng lọc',
        'PHÂN CHI NHÁNH': 'Phân chi nhánh', 'PHAN CHI NHANH': 'Phân chi nhánh',
        'ĐÃ LIÊN HỆ': 'Đã liên hệ', 'DA LIEN HE': 'Đã liên hệ',
        'ĐÃ HẸN': 'Đã hẹn', 'DA HEN': 'Đã hẹn', 'ĐÃ HẸN PHỎNG VẤN': 'Đã hẹn',
        'PV1': 'PV1', 'PV2': 'PV2',
        'THỬ VIỆC': 'Thử việc', 'THU VIEC': 'Thử việc',
        'TỪ CHỐI': 'Từ chối', 'TU CHOI': 'Từ chối',
        'ĐÃ NHẬN VIỆC': 'Đã nhận việc', 'DA NHAN VIEC': 'Đã nhận việc', 'ONBOARDED': 'Đã nhận việc',
        'NHÓM TIỀM NĂNG': 'Nhóm tiềm năng', 'TALENT POOL': 'Nhóm tiềm năng',
        'DANH SÁCH ĐEN': 'Danh sách đen', 'BLACKLIST': 'Danh sách đen',
    }
    return aliases.get(v.upper(), v)


def normalize_source(v: str) -> str:
    v = v.strip()
    aliases = {
        'TOPCV': 'Trang tuyển dụng', 'TRANG TUYỂN DỤNG': 'Trang tuyển dụng',
        'FACEBOOK': 'Khác',
        'WALK-IN': 'Trực tiếp', 'TRỰC TIẾP': 'Trực tiếp',
        'LINKEDIN': 'LinkedIn',
        'EMAIL': 'Email',
        'GIỚI THIỆU': 'Giới thiệu', 'GIỚI THIỆU': 'Giới thiệu', 'REFERRAL': 'Giới thiệu',
        'KHÁC': 'Khác',
    }
    return aliases.get(v.upper(), v)


def validate(candidate: dict) -> list:
    errors = []
    if not candidate.get('full_name'):
        errors.append('Thiếu ho ten')
    if not candidate.get('phone'):
        errors.append('Thiếu SDT')
    if not candidate.get('email'):
        errors.append('Thiếu email')
    if candidate.get('position_applied') not in POSITIONS:
        errors.append(f"Vi tri khong hop le: {candidate.get('position_applied')}")
    if candidate.get('assigned_branch') not in BRANCHES:
        errors.append(f"Chi nhanh khong hop le: {candidate.get('assigned_branch')}")
    if candidate.get('stage') not in STAGES:
        errors.append(f"Stage khong hop le: {candidate.get('stage')}")
    if candidate.get('source') not in SOURCE_LABELS:
        errors.append(f"Nguon khong hop le: {candidate.get('source')}")
    return errors


def next_id() -> str:
    candidates = json.loads(CANDIDATES_FILE.read_text(encoding='utf-8'))
    nums = [int(re.sub(r'\D', '', c.get('candidate_id', 'C0'))) for c in candidates]
    return f"C{max(nums or [0]) + 1:03d}"


def parse_multiline(text: str) -> dict | None:
    data = {}
    for line in text.splitlines():
        if ':' in line:
            k, v = line.split(':', 1)
            data[k.strip().lower()] = v.strip()
    if not data.get('ho ten'):
        return None
    candidate = {
        'candidate_id': next_id(),
        'created_at': date.today().isoformat(),
        'updated_at': date.today().isoformat(),
        'full_name': data.get('ho ten', '').strip(),
        'phone': data.get('sdt', '').strip(),
        'email': data.get('email', '').strip(),
        'zalo': data.get('sdt', '').strip(),
        'position_applied': normalize_position(data.get('vi tri', '')),
        'preferred_branch': normalize_branch(data.get('chi nhanh', '')),
        'assigned_branch': normalize_branch(data.get('chi nhanh', '')),
        'branch_flexibility': False,
        'region_preference': '',
        'source': normalize_source(data.get('nguon', 'Khác')),
        'cv_link': data.get('cv', ''),
        'experience_years': 0,
        'current_company': '',
        'expected_salary': '',
        'available_date': '',
        'english_level': '',
        'license_status': '',
        'stage': normalize_stage(data.get('stage', 'Mới')),
        'status': 'active',
        'owner': data.get('owner', ''),
        'next_action': data.get('next action', data.get('next_action', '')),
        'next_follow_up_date': '',
        'interview_date': '',
        'interviewer': '',
        'screening_score': 0,
        'interview_score': 0,
        'trial_score': 0,
        'final_score': 0,
        'decision': '',
        'offer_salary': '',
        'onboard_date': '',
        'notes': data.get('notes', ''),
    }
    return candidate


def parse_csv(text: str) -> dict | None:
    text = re.sub(r'^/add\s*', '', text.strip(), flags=re.IGNORECASE).strip()
    parts = [p.strip() for p in text.split(',')]
    if len(parts) < 4:
        return None
    return {
        'candidate_id': parts[0] if parts[0].upper().startswith('C') else next_id(),
        'created_at': date.today().isoformat(),
        'updated_at': date.today().isoformat(),
        'full_name': parts[1],
        'phone': parts[2],
        'email': parts[3],
        'zalo': parts[2],
        'position_applied': normalize_position(parts[4] if len(parts) > 4 else ''),
        'preferred_branch': normalize_branch(parts[5] if len(parts) > 5 else ''),
        'assigned_branch': normalize_branch(parts[5] if len(parts) > 5 else ''),
        'branch_flexibility': False,
        'region_preference': '',
        'source': normalize_source(parts[6] if len(parts) > 6 else 'Khác'),
        'cv_link': parts[7] if len(parts) > 7 else '',
        'experience_years': 0,
        'current_company': '',
        'expected_salary': '',
        'available_date': '',
        'english_level': '',
        'license_status': '',
        'stage': normalize_stage(parts[7] if len(parts) > 7 else 'Mới') if len(parts) > 7 else 'Mới',
        'status': 'active',
        'owner': parts[8] if len(parts) > 8 else '',
        'next_action': parts[9] if len(parts) > 9 else '',
        'next_follow_up_date': '',
        'interview_date': '',
        'interviewer': '',
        'screening_score': 0,
        'interview_score': 0,
        'trial_score': 0,
        'final_score': 0,
        'decision': '',
        'offer_salary': '',
        'onboard_date': '',
        'notes': '',
    }


def check_duplicate(phone: str, email: str, candidate_id: str | None = None) -> list:
    candidates = json.loads(CANDIDATES_FILE.read_text(encoding='utf-8'))
    dup = []
    for c in candidates:
        if candidate_id and c.get('candidate_id') == candidate_id:
            continue
        if phone and c.get('phone') == phone:
            dup.append(f"Trung SDT {phone} voi {c.get('full_name')} ({c.get('candidate_id')})")
        if email and c.get('email') == email:
            dup.append(f"Trung Email {email} voi {c.get('full_name')} ({c.get('candidate_id')})")
    return dup


def save(candidate: dict) -> dict:
    candidates = json.loads(CANDIDATES_FILE.read_text(encoding='utf-8'))
    candidates.append(candidate)
    CANDIDATES_FILE.write_text(json.dumps(candidates, ensure_ascii=False, indent=2), encoding='utf-8')
    return candidate


def publish() -> str:
    import subprocess
    result = subprocess.run(
        ['python3', str(ROOT / 'scripts' / 'publish_recruitment_dashboard.py')],
        capture_output=True, text=True, cwd=str(ROOT)
    )
    return result.stdout.strip() if result.returncode == 0 else result.stderr.strip()


def process(text: str) -> str:
    text = text.strip()
    if not text:
        return 'Thieu du lieu ung vien'
    if text.lower().startswith('/them_ung_vien') or '\n' in text and ':' in text:
        candidate = parse_multiline(text)
    else:
        candidate = parse_csv(text)

    if not candidate:
        return 'Format khong dung. Dung /them_ung_vien ... hoac /add C011,Ten,SDT,Email,LT,LCP,TopCV,Moi,HR,Gọi điện'

    errors = validate(candidate)
    if errors:
        return 'Loi nhap lieu:\n' + '\n'.join(f'- {e}' for e in errors)

    dups = check_duplicate(candidate.get('phone', ''), candidate.get('email', ''), candidate.get('candidate_id'))
    if dups:
        return 'Trung lap:\n' + '\n'.join(f'- {d}' for d in dups) + '\n\nNeu muon tiep tuc thi them --force'

    if '--force' in text:
        candidate = save(candidate)
        out = publish()
        return f'Da them (force): {candidate["candidate_id"]} - {candidate["full_name"]}\n{out}'
    else:
        preview = f'Xac nhan them ung vien:\n- ID: {candidate["candidate_id"]}\n- Ho ten: {candidate["full_name"]}\n- SDT: {candidate["phone"]}\n- Email: {candidate["email"]}\n- Vi tri: {candidate["position_applied"]}\n- Chi nhanh: {candidate["assigned_branch"]}\n- Nguon: {candidate["source"]}\n- Stage: {candidate["stage"]}\n- Owner: {candidate["owner"]}\n\nTra loi: OK'
        return preview

    return candidate


if __name__ == '__main__':
    text = ' '.join(sys.argv[1:]) if len(sys.argv) > 1 else ''
    if not text:
        print('Usage: python3 telegram_candidate_input.py "<message>"')
        sys.exit(1)
    print(process(text))
