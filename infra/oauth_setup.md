# Gmail OAuth Setup

This project uses OAuth 2.0 to access a user's Gmail inbox.

## 1. Configure the OAuth Consent Screen

1. Visit [OAuth Consent Screen](https://console.cloud.google.com/apis/credentials/consent).
2. Choose **External** for the user type.
3. Provide an application name such as `Gmail PDF Pipeline` and complete the remaining fields.
4. In **Test users**, add your Gmail address.

⚠️ Without adding yourself as a test user you will get `Access blocked: This app has not been verified` errors.

## 2. Create a Desktop OAuth Client

1. Go to [Credentials](https://console.cloud.google.com/apis/credentials).
2. Select **Create credentials → OAuth client ID**.
3. Choose **Desktop App** and name it (e.g. `Gmail PDF Intake – Desktop`).
4. Download the generated `credentials.json` file and place it in the project root.

## 3. Authorize the Gmail Account

Run the authorization script to generate `token.pickle`:

```bash
python gmail/authorize_gmail.py
```

The script opens a browser window, prompts for Gmail access and saves a `token.pickle` file with long‑term credentials.

The default scope used is `https://www.googleapis.com/auth/gmail.readonly`. To modify messages, use `https://www.googleapis.com/auth/gmail.modify` instead.

After generating the token, follow the [Secret Manager setup](secrets_setup.md) guide to store it securely for the Cloud Function.
