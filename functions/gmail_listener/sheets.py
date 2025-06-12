from googleapiclient.discovery import build
import google.auth
import os

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SHEET_NAME = "AI Email Processing Dashboard"
SHEET_ID = os.getenv("SHEET_ID")


def get_sheets_service():
    # Use Application Default Credentials (ADC) provided by Cloud Functions
    credentials, _ = google.auth.default(scopes=SCOPES)
    return build('sheets', 'v4', credentials=credentials)


def create_dashboard_sheet():
    service = get_sheets_service()
    spreadsheet = {
        'properties': {
            'title': SHEET_NAME
        },
        'sheets': [
            {'properties': {'title': 'Emails'}},
            {'properties': {'title': 'Attachments'}}
        ]
    }

    spreadsheet = service.spreadsheets().create(body=spreadsheet, fields='spreadsheetId').execute()
    print(f"Created spreadsheet with ID: {spreadsheet['spreadsheetId']}")
    return spreadsheet['spreadsheetId']


def append_email_row(sheet_id, row):
    service = get_sheets_service()
    values = [row]
    body = {'values': values}
    service.spreadsheets().values().append(
        spreadsheetId=sheet_id,
        range='Emails!A1',
        valueInputOption='RAW',
        body=body
    ).execute()


def append_document_row(sheet_id, row):
    service = get_sheets_service()
    values = [row]
    body = {'values': values}
    service.spreadsheets().values().append(
        spreadsheetId=sheet_id,
        range='Attachments!A1',
        valueInputOption='RAW',
        body=body
    ).execute()


def get_processed_message_ids(sheet_id):
    service = get_sheets_service()
    result = service.spreadsheets().values().get(
        spreadsheetId=sheet_id,
        range="Emails!H2:H"
    ).execute()

    values = result.get("values", [])
    return set(row[0] for row in values if row)
