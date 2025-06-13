# Google Cloud Setup

This document covers the initial Google Cloud configuration for the PDF Intake Pipeline.

## 1. Create a Project

1. Open the [Google Cloud Console](https://console.cloud.google.com/).
2. Create a new project (e.g. `gmail-doc-processing`).
3. Associate the project with a billing account.
4. Note the **Project ID** for later commands.

## 2. Enable Required APIs

Enable these APIs in your project:

- Gmail API
- Pub/Sub API
- Cloud Functions API
- Document AI API
- Vertex AI API
- Cloud Storage API (optional)
- IAM API
- Sheets API
- Secret Manager API
- Cloud Run API
- Cloud Build API
- Eventarc API

Use the CLI to enable them all:

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
  eventarc.googleapis.com
```

## 3. Create a Service Account

Create a dedicated account for Cloud Functions and API access:

```bash
gcloud iam service-accounts create gmail-function-sa \
  --display-name="Service account for Gmail PDF Processing"
```

Grant it the required roles:

```bash
PROJECT_ID=$(gcloud config get-value project)

for ROLE in roles/pubsub.publisher \
            roles/cloudfunctions.invoker \
            roles/documentai.apiUser \
            roles/aiplatform.user \
            roles/storage.objectAdmin; do
  gcloud projects add-iam-policy-binding "$PROJECT_ID" \
    --member="serviceAccount:gmail-function-sa@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="$ROLE"
done
```
