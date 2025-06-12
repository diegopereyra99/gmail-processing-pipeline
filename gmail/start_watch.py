import pickle
from googleapiclient.discovery import build

# Path to your token.pickle (from the OAuth flow)
TOKEN_PATH = 'token.pickle'
PROJECT_ID = 'gmail-doc-processing'

# Your full Pub/Sub topic name:
TOPIC_NAME = f'projects/{PROJECT_ID}/topics/gmail-watch'

def main():
    with open(TOKEN_PATH, 'rb') as token:
        creds = pickle.load(token)

    service = build('gmail', 'v1', credentials=creds)

    watch_request = {
        'labelIds': ['INBOX'], # Change this to the labels you want to watch
        'topicName': TOPIC_NAME
    }

    response = service.users().watch(userId='me', body=watch_request).execute()
    print("✅ Gmail watch started!")
    print("Response:", response)

if __name__ == '__main__':
    main()
