import base64
import json
import pickle
import os
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google.cloud import secretmanager
from sheets import append_email_row, append_document_row, get_processed_message_ids
from gemini_utils import summarize_email_structured, analyze_attachment


def fetch_last_messages(service, count=5):
    results = service.users().messages().list(userId='me', maxResults=count, labelIds=["INBOX"]).execute()
    return results.get("messages", [])


def get_gmail_service():
    secret_client = secretmanager.SecretManagerServiceClient()
    secret_name = "projects/pdfanalysis-451621/secrets/gmail-token/versions/latest"
    response = secret_client.access_secret_version(request={"name": secret_name})
    token_data = response.payload.data
    creds = pickle.loads(token_data)

    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())

    return build('gmail', 'v1', credentials=creds)


def extract_attachments(service, msg_id, parts):
    attachments = []

    for part in parts:
        filename = part.get("filename", "")
        mime_type = part.get("mimeType", "application/octet-stream")

        if not filename:
            continue

        file_data = None

        if "data" in part["body"]:
            # print(f"📎 Inline attachment found: {filename}")
            file_data = base64.urlsafe_b64decode(part["body"]["data"])
        elif "attachmentId" in part["body"]:
            # print(f"📎 Fetching attachment from Gmail API: {filename}")
            attachment = service.users().messages().attachments().get(
                userId="me",
                messageId=msg_id,
                id=part["body"]["attachmentId"]
            ).execute()
            file_data = base64.urlsafe_b64decode(attachment["data"])

        if file_data:
            attachments.append({
                "filename": filename,
                "mime_type": mime_type,
                "data": file_data,
            })

    return attachments


def gmail_pubsub_trigger(event, context):
    print("📬 Triggered by Gmail Pub/Sub message")
    data = base64.b64decode(event['data']).decode('utf-8')
    pubsub_message = json.loads(data)
    history_id = pubsub_message.get("historyId")

    if not history_id:
        print("⚠️ No historyId in Pub/Sub message.")
        return

    print(f"🔍 Processing historyId: {history_id}")
    
    service = get_gmail_service()
    SHEET_ID = os.getenv("SHEET_ID")
    # print(f"📄 Target Google Sheet ID: {SHEET_ID}")

    try:
        processed_ids = get_processed_message_ids(SHEET_ID)

        latest_messages = fetch_last_messages(service)

        for meta in latest_messages:
            msg_id = meta["id"]
            if msg_id in processed_ids:
                print(f"✅ Message {msg_id} already processed.")
                continue

            msg = service.users().messages().get(userId="me", id=msg_id, format="full").execute()

            headers = {h['name']: h['value'] for h in msg['payload'].get('headers', [])}
            subject = headers.get("Subject", "(no subject)")
            sender = headers.get("From", "unknown")
            date = headers.get("Date", "unknown")

            print(f"✉️ Processing email: {subject} from {sender} on {date}")

            email_summary = summarize_email_structured(msg)

            append_email_row(SHEET_ID, [
                date,
                sender,
                subject,
                email_summary["summary"],
                email_summary.get("tag", ""),
                email_summary.get("action_required", "unknown"),
                f"https://mail.google.com/mail/u/0/#inbox/{msg_id}",
                msg_id,
            ])

            parts = msg['payload'].get('parts', [])
            attachments = extract_attachments(service, msg_id, parts)

            for attachment in attachments:
                print(f"📄 Analyzing attachment: {attachment['filename']}")
                doc = analyze_attachment(**attachment)

                append_document_row(SHEET_ID, [
                    attachment["filename"],
                    subject,
                    doc.get("type", "unknown"),
                    doc.get("summary", "n/a"),
                    doc.get("total", ""),
                    doc.get("date", ""),
                    f"https://mail.google.com/mail/u/0/#inbox/{msg_id}"
                ])
    except Exception as e:
        print(f"❌ Error processing message: {e}")