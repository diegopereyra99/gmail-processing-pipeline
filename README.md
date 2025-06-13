# PDF Intake Pipeline

This project automates processing of PDF email attachments with Google Cloud. Gmail events trigger a Cloud Function that downloads new messages, parses PDFs with Document AI and Gemini, and logs the results to Google Sheets.

## Repository Layout

- `functions/gmail_listener` – Cloud Function source code
- `gmail/` – Gmail API utilities and watch helpers
- `scripts/` – Local testing utilities
- `infra/` – Infrastructure setup guides
- `docs/` – Local development notes

## Setup Overview

1. **Google Cloud Setup** – create a project, enable APIs and configure a service account. [See instructions](infra/google_cloud_setup.md)
2. **Gmail OAuth** – register an OAuth client and authorize your Gmail account. [See instructions](infra/oauth_setup.md)
3. **Secret Manager** – upload the Gmail token for the function to use. [See instructions](infra/secrets_setup.md)
4. **Gmail Watch & Pub/Sub** – create a Pub/Sub topic and register a watch. [See instructions](infra/pubsub_setup.md)
5. **Deploy the Gmail Listener** – build and deploy the Cloud Function. [See instructions](functions/gmail_listener/README.md)
6. **Local Setup** – install dependencies and run local helpers. [See instructions](docs/local_setup.md)

Follow each guide in order to deploy the pipeline on your own Google Cloud project.
