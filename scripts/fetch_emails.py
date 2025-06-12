from googleapiclient.discovery import build
from google.auth.transport.requests import Request
import pickle
import base64
import json

# Load Gmail credentials
def get_service():
    with open("gmail/token.pickle", "rb") as f:
        creds = pickle.load(f)
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
    return build("gmail", "v1", credentials=creds)

# Fetch last N messages
def fetch_messages(service, max_results=10):
    results = service.users().messages().list(userId='me', maxResults=max_results).execute()
    messages = results.get('messages', [])
    return [service.users().messages().get(userId='me', id=msg['id'], format='full').execute() for msg in messages]

# Save message data to local files
def save_messages(messages):
    for msg in messages:
        with open(f"emails/{msg['id']}.json", "w") as f:
            json.dump(msg, f, indent=2)

if __name__ == "__main__":
    import os
    os.makedirs("emails", exist_ok=True)
    service = get_service()
    msgs = fetch_messages(service, max_results=10)  # you can increase this
    save_messages(msgs)
    print(f"✅ Saved {len(msgs)} emails to /emails")
