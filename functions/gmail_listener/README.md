# Gmail Listener Cloud Function

This function is triggered by Pub/Sub messages from Gmail. It downloads new emails and processes PDF attachments using Document AI and Gemini, then records the results in a Google Sheet.

## Structure

```
functions/
└── gmail_listener/
    ├── gemini_utils.py
    ├── main.py                # Entry point
    ├── requirements.txt
    └── sheets.py
```

## Entry Point

The deployed function uses `gmail_pubsub_trigger` from `main.py` as its entry point.

## Environment Variables

`SHEET_ID` must be provided at deployment time and points to the spreadsheet that will store parsed data.

## Deployment

```bash
gcloud functions deploy gmail_pubsub_trigger \
  --runtime python310 \
  --trigger-topic gmail-watch \
  --entry-point gmail_pubsub_trigger \
  --source functions/gmail_listener \
  --service-account gmail-function-sa@<YOUR_PROJECT_ID>.iam.gserviceaccount.com \
  --set-env-vars SHEET_ID=<YOUR_SHEET_ID>,PROJECT_ID=<YOUR_PROJECT_ID> \
  --memory 512MB \
  --timeout 60s
```

If invocation permissions are required for Cloud Run, run:

```bash
gcloud run services add-iam-policy-binding gmail-pubsub-trigger \
  --region=us-central1 \
  --member="allUsers" \
  --role="roles/run.invoker"
```

After deployment the function automatically triggers on new Gmail events, downloads attachments and writes results to the configured Google Sheet.
