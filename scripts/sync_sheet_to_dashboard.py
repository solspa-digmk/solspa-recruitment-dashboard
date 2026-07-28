#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Sync Recruitment Candidate Input Sheet -> candidates.json -> publish dashboard.

Usage:
  python3 sync_sheet_to_dashboard.py
"""

from __future__ import annotations

import json
import re
import sys
from datetime import date
from pathlib import Path

try:
    from google.oauth2 import service_account
    from googleapiclient.discovery import build
except ImportError:
    print(
        'Missing google-auth/oauth2. Install with: pip install google-api-python-client google-auth',
        file=sys.stderr,
    )
    sys.exit(1)

ROOT = Path('/Users/giangvu/.hermes/repos/solspa-recruitment-dashboard')
DATA = ROOT / 'data'
CANDIDATES_FILE = DATA / 'candidates.json'
SERVICE_ACCOUNT_FILE = Path('/Users/giangvu/.hermes/solspa-dashboard-sync-4554633aab66.json')
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
SHEET_ID = '1hs0gjgwjeUHJUK1qm5J9fuB4K4H1EIaFRhjyNLal7FE'
TAB_NAME = 'Candidate_Input'

POSITIONS = {'PGD', 'QLCN', 'LT', 'BS', 'TLV'}
BRANCHES = {'Q7', 'LCP', 'LCR', 'RNS', 'MVT', 'MBC', 'LR', 'HM', 'DL'}
STAGES = {
    'Mới', 'Sàng lọc', 'Phân chi nhánh', 'Đã liên hệ', 'Đã hẹn',
    'PV1', 'PV2', 'Thử việc', 'Từ chối', 'Đã nhận việc',
    'Nhóm tiềm năng', 'Danh sách đen'
}
SOURCE_LABELS = {'Giới thiệu', 'Trang tuyển dụng', 'LinkedIn', 'Email', 'Trực tiếp', 'Khác'}


def normalize_position(v: str) -> str:
    v = v.strip().upper()
    mapping = {
        'QUẢN LÝ/PHÓ QUẢN LÝ CHI NHÁNH': 'QLCN',
        'BÁC SĨ/Y SĨ': 'BS',
        'TRỊ LIỆU VIÊN': 'TLV',
        'LỄ TÂN': 'LT',
        'PHÓ GIÁM ĐỐC': 'PGD',
    }
    return mapping.get(v, v)


def normalize_branch(v: str) -> str:
    v = v.strip().upper()
    mapping = {
        'PHÒNG KHÁM Q7': 'Q7',
        'MERCURE VT': 'MVT',
        'MINERA BÌNH CHÂU': 'MBC',
        'LAN RỪNG': 'LR',
        'HOÀN MỸ': 'HM',
        'ĐÀ LẠT': 'DL',
    }
    return mapping.get(v, v)


def normalize_stage(v: str) -> str:
    v = v.strip()
    aliases = {
        'MỚI': 'Mới', 'MỚI': 'Mới', 'MOI': 'Mới',
        'SÀNG LỌC': 'Sàng lọc', 'PHÂN CHI NHÁNH': 'Phân chi nhánh',
        'ĐÃ LIÊN HỆ': 'Đã liên hệ', 'ĐÃ HẸN': 'Đã hẹn',
        'THỬ VIỆC': 'Thử việc', 'TỪ CHỐI': 'Từ chối',
        'ĐÃ NHẬN VIỆC': 'Đã nhận việc', 'ONBOARDED': 'Đã nhận việc',
        'NHÓM TIỀM NĂNG': 'Nhóm tiềm năng', 'TALENT POOL': 'Nhóm tiềm năng',
        'DANH SÁCH ĐEN': 'Danh sách đen', 'BLACKLIST': 'Danh sách đen',
    }
    return aliases.get(v.upper(), v)


def normalize_source(v: str) -> str:
    v = v.strip()
    aliases = {
        'TOPCV': 'Trang tuyển dụng',
        'FACEBOOK': 'Khác',
        'WALK-IN': 'Trực tiếp', 'TRỰC TIẾP': 'Trực tiếp',
        'LINKEDIN': 'LinkedIn',
        'EMAIL': 'Email',
        'GIỚI THIỆU': 'Giới thiệu', 'GIỚI THIỆU': 'Giới thiệu', 'REFERRAL': 'Giới thiệu',
        'KHÁC': 'Khác',
    }
    return aliases.get(v.upper(), v)


def next_id() -> str:
    candidates = json.loads(CANDIDATES_FILE.read_text(encoding='utf-8'))
    nums = [int(re.sub(r'\D', '', c.get('candidate_id', 'C0'))) for c in candidates]
    return f'C{max(nums or [0]) + 1:03d}'


def check_duplicate(phone: str, email: str, candidate_id: str | None = None) -> list[str]:
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


def parse_row(row: dict[str, str]) -> dict:
    cid = (row.get('ID') or next_id()).strip()
    phone = str(row.get('SDT', '')).strip()
    email = str(row.get('Email', '')).strip()
    stage = normalize_stage(row.get('Stage', 'Mới'))
    source = normalize_source(row.get('Nguon', 'Khác'))
    position = normalize_position(row.get('Vi_tri', ''))
    branch = normalize_branch(row.get('Chi_nhanh', ''))
    expected_salary_raw = re.sub(r'\D', '', row.get('Expected_salary', '') or '0')
    expected_salary = int(expected_salary_raw or 0)

    candidate = {
        'candidate_id': cid,
        'created_at': row.get('Created_at') or date.today().isoformat(),
        'updated_at': row.get('Updated_at') or date.today().isoformat(),
        'full_name': row.get('Ho_ten', '').strip(),
        'phone': phone,
        'email': email,
        'zalo': phone,
        'position_applied': position,
        'preferred_branch': branch,
        'assigned_branch': branch,
        'branch_flexibility': False,
        'region_preference': row.get('Region', '').strip(),
        'source': source,
        'cv_link': row.get('CV', '').strip(),
        'experience_years': int(row.get('Exp_years') or 0),
        'current_company': row.get('Current_company', '').strip(),
        'expected_salary': expected_salary,
        'available_date': row.get('Available_date', '').strip(),
        'english_level': row.get('English', '').strip(),
        'license_status': row.get('License', '').strip(),
        'stage': stage,
        'status': 'active' if stage not in {'Từ chối', 'Danh sách đen'} else 'closed',
        'owner': row.get('Owner', '').strip(),
        'next_action': row.get('Next_action', '').strip(),
        'next_follow_up_date': row.get('Next_follow', '').strip(),
        'interview_date': row.get('Interview_date', '').strip(),
        'interviewer': row.get('Interviewer', '').strip(),
        'screening_score': int(row.get('Score_screening') or 0),
        'interview_score': int(row.get('Score_interview') or 0),
        'trial_score': int(row.get('Score_trial') or 0),
        'final_score': int(row.get('Score_final') or 0),
        'decision': row.get('Decision', '').strip(),
        'offer_salary': row.get('Offer_salary', '').strip(),
        'onboard_date': row.get('Onboard_date', '').strip(),
        'notes': row.get('Notes', '').strip(),
    }
    return candidate


def validate_row(row: dict) -> list[str]:
    errors = []
    if not row.get('full_name'):
        errors.append('Thiếu Ho_ten')
    if not row.get('phone'):
        errors.append('Thiếu SDT')
    if not row.get('email'):
        errors.append('Thiếu Email')
    if row.get('position_applied') not in POSITIONS:
        errors.append(f"Vi_tri khong hop le: {row.get('position_applied')}")
    if row.get('assigned_branch') not in BRANCHES:
        errors.append(f"Chi_nhanh khong hop le: {row.get('assigned_branch')}")
    if row.get('stage') not in STAGES:
        errors.append(f"Stage khong hop le: {row.get('stage')}")
    if row.get('source') not in SOURCE_LABELS:
        errors.append(f"Nguon khong hop le: {row.get('source')}")
    return errors


def read_sheet() -> list[dict]:
    if not SERVICE_ACCOUNT_FILE.exists():
        raise FileNotFoundError(f'Missing service account file: {SERVICE_ACCOUNT_FILE}')

    creds = service_account.Credentials.from_service_account_file(
        str(SERVICE_ACCOUNT_FILE), scopes=SCOPES
    )
    svc = build('sheets', 'v4', credentials=creds)

    all_rows: list[dict] = []

    for tab in [TAB_NAME, 'Candidate_Telegram_Input']:
        resp = svc.spreadsheets().values().get(spreadsheetId=SHEET_ID, range=f"'{tab}'!A1:Z500").execute()
        values = resp.get('values', [])
        if not values:
            continue

        headers = [str(h).strip() if h else '' for h in values[0]]

        for r in values[1:]:
            if not any(v.strip() for v in r):
                continue
            row = {headers[i]: (r[i] if i < len(r) else '') for i in range(len(headers))}

            # Normalize Telegram simple format to standard keys
            if tab == 'Candidate_Telegram_Input':
                row['CV'] = ''
                row['Owner'] = row.get('Owner', '')
                row['Next_action'] = row.get('Next_action', '')
                row['Notes'] = ''
                row['Created_at'] = ''
                row['Updated_at'] = ''

            all_rows.append(row)

    return all_rows


def sync() -> tuple[list[dict], list[dict], str]:
    raw_rows = read_sheet()
    if not raw_rows:
        print('Khong co du lieu trong tab nhap.')
        return [], [], 'NO_CHANGE'

    candidates = json.loads(CANDIDATES_FILE.read_text(encoding='utf-8'))
    appended = []
    errors = []

    seen_ids = {c.get('candidate_id') for c in candidates}

    for row in raw_rows:
        cid = (row.get('ID') or next_id()).strip()
        if cid in seen_ids:
            continue

        try:
            candidate = parse_row(row)
        except Exception as e:
            errors.append({'row': row, 'errors': [str(e)]})
            continue

        errs = validate_row(candidate)
        if errs:
            errors.append({'row': row, 'errors': errs})
            continue

        dups = check_duplicate(candidate['phone'], candidate['email'], candidate['candidate_id'])
        if dups:
            errors.append({'row': row, 'errors': dups})
            continue

        candidates.append(candidate)
        appended.append(candidate)
        seen_ids.add(candidate['candidate_id'])

    CANDIDATES_FILE.write_text(json.dumps(candidates, ensure_ascii=False, indent=2), encoding='utf-8')

    # Publish dashboard
    import subprocess
    result = subprocess.run(
        ['python3', str(ROOT / 'scripts' / 'publish_recruitment_dashboard.py')],
        capture_output=True,
        text=True,
        cwd=str(ROOT),
    )
    publish_output = result.stdout.strip() if result.returncode == 0 else result.stderr.strip()

    return appended, errors, publish_output


def main():
    print('Syncing Candidate_Input + Candidate_Telegram_Input -> candidates.json -> dashboard...')
    try:
        appended, errors, publish_output = sync()
    except Exception as e:
        print(f'Loi: {e}', file=sys.stderr)
        sys.exit(1)

    print(f'Da them {len(appended)} ung vien')
    for c in appended:
        print(f"- {c['candidate_id']} | {c['full_name']} | {c['phone']} | {c['email']}")

    if errors:
        print('\nCac dong bi loi/bo qua:')
        for err in errors:
            row = err['row']
            print(f"- {row.get('Ho_ten','?')} | {row.get('SDT','?')} | {err['errors']}")

    print('\nPublish dashboard:')
    print(publish_output or 'NO_CHANGE')


if __name__ == '__main__':
    main()
