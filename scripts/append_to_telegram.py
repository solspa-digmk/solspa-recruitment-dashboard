import sys
from pathlib import Path
from google.oauth2 import service_account
from googleapiclient.discovery import build

SERVICE_ACCOUNT_FILE = Path('/Users/giangvu/.hermes/solspa-dashboard-sync-4554633aab66.json')
SHEET_ID = '1hs0gjgwjeUHJUK1qm5J9fuB4K4H1EIaFRhjyNLal7FE'
TAB_NAME = 'Candidate_Telegram_Input'
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

def append_row(data_list):
    creds = service_account.Credentials.from_service_account_file(str(SERVICE_ACCOUNT_FILE), scopes=SCOPES)
    svc = build('sheets', 'v4', credentials=creds)
    body = {'values': [data_list]}
    svc.spreadsheets().values().append(
        spreadsheetId=SHEET_ID,
        range=f"'{TAB_NAME}'!A1",
        valueInputOption='RAW',
        body=body
    ).execute()

if __name__ == "__main__":
    # Correct columns: ID, Ho_ten, SDT, Email, Vi_tri, Chi_nhanh, Nguon, Stage, Owner, Next_action
    if len(sys.argv) < 10:
        print("Usage: python3 append_to_telegram.py ID Ho_ten SDT Email Vi_tri Chi_nhanh Nguon Stage Owner Next_action")
        sys.exit(1)
    append_row(sys.argv[1:])
    print("Success")
