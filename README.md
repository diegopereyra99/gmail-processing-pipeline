# PDF Intake Pipeline

This project automates Gmail-to-DocumentAI-to-Gemini PDF processing using Google Cloud Functions.

## Structure

- `functions/gmail_listener/`: Gmail trigger Cloud Function
- `notebooks/`: Experimentation (Gemini, Document AI)
- `scripts/`: Local dev/testing
- `gmail/`: Gmail API utils, auth, message parsing
- `infra/`: Setup docs for secrets, Pub/Sub, etc.

## Local Setup

```bash
pip install -r requirements.txt
```

## Set up on Google Cloud

### Step 1 – Google Cloud Project Setup

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project: **gmail-doc-processing** (or similar)
3. Associate it with a billing account
4. Note down the **Project ID**, which will be used throughout the pipeline

### Step 2 – Enable Required APIs

Enable the following Google Cloud APIs for your project:

- Gmail API
- Pub/Sub API
- Cloud Functions API
- Document AI API
- Vertex AI API (Gemini)
- Cloud Storage API (optional)
- IAM API
- Sheets API

You can enable them all at once via CLI:

```bash
gcloud config set project <YOUR_PROJECT_ID>

gcloud services enable \
  gmail.googleapis.com \
  pubsub.googleapis.com \
  cloudfunctions.googleapis.com \
  documentai.googleapis.com \
  aiplatform.googleapis.com \
  storage.googleapis.com \
  iam.googleapis.com \
  secretmanager.googleapis.com \
  sheets.googleapis.com \
  run.googleapis.com \
  cloudbuild.googleapis.com \
  eventarc.googleapis.com# PDF Intake Pipeline
```

## Step 3 – Create a Service Account

Create a dedicated service account for Cloud Functions and API access:

```bash
gcloud iam service-accounts create gmail-function-sa \
  --display-name="Service account for Gmail PDF Processing"
```

Assign the following roles:

```bash
PROJECT_ID=$(gcloud config get-value project)

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:gmail-function-sa@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/pubsub.publisher"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:gmail-function-sa@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/cloudfunctions.invoker"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:gmail-function-sa@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/documentai.apiUser"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:gmail-function-sa@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/aiplatform.user"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:gmail-function-sa@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/storage.objectAdmin"
```

### Step 4 – Set Up OAuth for Gmail API Access

To access a user's Gmail inbox and download attachments, you must configure OAuth 2.0. This step is crucial and involves 3 substeps.

---

#### 4.1 – Configure the OAuth Consent Screen

1. Go to [OAuth Consent Screen](https://console.cloud.google.com/apis/credentials/consent)
2. Select **"External"** as the user type
3. Fill in the following:
   - App name: `Gmail PDF Pipeline`
   - User support email: your Gmail address
   - Developer contact info: your Gmail address
4. In the "Test users" section, **add your own Gmail** 
5. Save and complete the setup

> ⚠️ If you don't add yourself as a test user, you'll receive a 403 error like:
> `Access blocked: This app has not been verified`

---

#### 4.2 – Create an OAuth Client (Desktop App)

1. Go to [Credentials](https://console.cloud.google.com/apis/credentials)
2. Click **Create Credentials → OAuth Client ID**
3. Choose **"Desktop App"** as the application type
4. Name it something like `Gmail PDF Intake – Desktop`
5. Download the `credentials.json` file
6. Place it inside your project folder

---

#### 4.3 – Authorize the Gmail Account

Use the script `authorize_gmail.py` to initiate the OAuth flow and generate a `token.pickle` file.

```bash
python ./gmail/authorize_gmail.py
```

The script will:
- Open your default browser
- Ask for permission to access your Gmail inbox
- Save a `token.pickle` file with long-term access credentials
- Print the authorized Gmail address to confirm success

> You only need to run this once per account, unless the token expires or you change scopes.

---
#### Notes

This project uses the **read-only** Gmail API scope:

```python
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
```

> If you need to move/delete emails in the future, replace with:
> `https://www.googleapis.com/auth/gmail.modify`

At this point you can try fetching messages using the script `scripts/fetch_emails.py`.

---

#### ✅ Result

After this step, you will have:
- `credentials.json`: your OAuth client credentials
- `token.pickle`: a persistent token that allows programmatic access to Gmail

## Step 4.5 – Store `token.pickle` in Secret Manager

After generating the `token.pickle` file in Step 4, you should store it securely in Google Secret Manager. This allows your Cloud Function to access Gmail without including sensitive files in the deployment.

---

### 🔐 1. Enable the Secret Manager API (if needed)

If prompted, accept when Google Cloud CLI asks to enable it, or do it manually:

```bash
gcloud services enable secretmanager.googleapis.com --project=<YOUR_PROJECT_ID>
```

---

### 🔐 2. Create a new secret

Run this command to create a secret named `gmail-token`:

```bash
gcloud secrets create gmail-token   --replication-policy="automatic"   --project=<YOUR_PROJECT_ID>
```

---

### 📤 3. Upload your `token.pickle` file

After creating the secret, upload your local `token.pickle` as a secret version:

```bash
gcloud secrets versions add gmail-token   --data-file=token.pickle   --project=<YOUR_PROJECT_ID>
```

> This securely stores the token for use by your Cloud Function.

---

### 🔑 4. Grant access to the Cloud Function

Make sure the Cloud Function’s service account has permission to access secrets:

```bash
gcloud projects add-iam-policy-binding <YOUR_PROJECT_ID> \
  --member="serviceAccount:<YOUR_SERVICE_ACCOUNT_EMAIL>" \
  --role="roles/secretmanager.secretAccessor"
```

---

### ✅ Usage in the Cloud Function

Your function can now load the token like this:

```python
from google.cloud import secretmanager
import pickle

secret_client = secretmanager.SecretManagerServiceClient()
secret_name = "projects/<YOUR_PROJECT_ID>/secrets/gmail-token/versions/latest"
response = secret_client.access_secret_version(request={"name": secret_name})
token_data = response.payload.data
creds = pickle.loads(token_data)
```

This allows secure and automatic access to Gmail from within your function.

### Step 5 – Set Up Gmail Watch + Pub/Sub

This step connects Gmail to your pipeline using Google Pub/Sub. When a new email arrives in your inbox, Gmail will publish a notification to a Pub/Sub topic.

---

#### 5.1 – Create a Pub/Sub Topic

Run the following command to create the topic:

```bash
gcloud pubsub topics create gmail-watch
```

---

#### 5.2 – Grant Gmail Permission to Publish

Gmail uses a special internal service account to publish notifications. Grant it permission:

```bash
gcloud pubsub topics add-iam-policy-binding gmail-watch \
  --member="serviceAccount:gmail-api-push@system.gserviceaccount.com" \
  --role="roles/pubsub.publisher"
```

---

#### 5.3 – Register a Gmail Watch

Use the provided script to register a Gmail watch that listens for new emails and sends events to Pub/Sub.

```bash
python ./gmail/start_watch.py
```

---

#### 🔁 Note on Expiration

Gmail watches **expire every 7 days**. You must re-run this script weekly or automate it with a cron job or Cloud Scheduler.

---

#### ✅ Result

Once the watch is registered:
- New emails in your inbox will trigger messages on the Pub/Sub topic
- You can connect this to a Cloud Function to begin processing automatically

## Step 6 – Deploy the Gmail Listener Cloud Function

This step deploys a Cloud Function that listens for new emails via Pub/Sub and processes them using Gmail API, Gemini, and Google Sheets.

---

### 📁 Function Structure

Your function should be organized like this:

```
functions/
└── gmail_listener/
    ├── gemini_utils.py
    ├── main.py                # Entry point: gmail_pubsub_trigger
    ├── requirements.txt
    ├── sheets.py
    ├── sheets-access-key.json (optional: recommended to use env vars or Secret Manager instead)
    └── __pycache__/ (ignored)
```

---

### 📌 Entry Point

The main handler function is defined in `main.py` as:

```python
def gmail_pubsub_trigger(event, context):
    ...
```

---

### ⚙️ Environment Variables

Your function uses:

```python
SHEET_ID = os.getenv("SHEET_ID")
```

This must be passed during deployment using `--set-env-vars`.

---

### 🚀 Deployment Command

```bash
gcloud functions deploy gmail_pubsub_trigger \
  --runtime python310  \
  --trigger-topic gmail-watch \
  --entry-point gmail_pubsub_trigger  \
  --source functions/gmail_listener \
  --service-account gmail-function-sa@gmail-doc-processing.iam.gserviceaccount.com \
  --set-env-vars SHEET_ID=1m7X-2a7EOPu9YhjjTy-CSi1H7A98w_NcsJRk1Pyn3Rc,PROJECT_ID=gmail-doc-processing \
  --memory 512MB \
  --timeout 60s
```

---

Maybe you need to run this:

```bash
gcloud run services add-iam-policy-binding gmail-pubsub-trigger \
  --region=us-central1 \
  --member="allUsers" \
  --role="roles/run.invoker"
```

### ✅ Result

This Cloud Function will:
- Trigger automatically when a new email arrives
- Download and process the email and its attachments
- Send structured results to a Google Sheet