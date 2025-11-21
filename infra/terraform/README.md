# Terraform Infrastructure

This configuration provisions the Google Cloud resources used by the Gmail processing pipeline:

- Enables all required APIs (Gmail, Pub/Sub, Cloud Functions, Document AI, Vertex AI, Secret Manager, Sheets, and others)
- Creates the Cloud Function service account with the roles required by the pipeline
- Creates the Pub/Sub topic that receives Gmail push notifications and grants Gmail permission to publish
- Creates the Secret Manager secret to store the Gmail OAuth token and grants the function access
- Packages and deploys the Gmail listener Cloud Function (Gen 2) with the appropriate environment variables

## Prerequisites

- [Terraform](https://developer.hashicorp.com/terraform/downloads) 1.6+
- Google Cloud credentials configured for the target project (e.g., via `gcloud auth application-default login`)
- A Google Sheets document already created for storing pipeline results
- A generated Gmail OAuth token (`token.pickle`) to upload to Secret Manager after deployment

> ℹ️ OAuth client creation and token generation cannot be automated with Terraform because they require interactive user
> consent in a browser. Follow [infra/oauth_setup.md](../oauth_setup.md) to create the OAuth client and generate
> `token.pickle`, then proceed with deployment.

## Usage

From the repository root:

```bash
cd infra/terraform
terraform init

terraform apply \
  -var "project_id=<YOUR_PROJECT_ID>" \
  -var "sheet_id=<YOUR_SHEET_ID>"
```

Key configurable variables:

- `project_id` (required): Target Google Cloud project ID
- `sheet_id` (required): Google Sheet ID used by the Gmail listener
- `region`: Deployment region for the Cloud Function and storage bucket (default: `us-central1`)
- `pubsub_topic`: Pub/Sub topic name for Gmail watch notifications (default: `gmail-watch`)
- `function_name`: Name for the deployed Cloud Function (default: `gmail-pubsub-trigger`)
- `function_source_bucket`: Override for the staging bucket used for the function source archive
- `gmail_token_secret_id`: Secret Manager ID for the Gmail OAuth token (default: `gmail-token`)

> ⚠️ The configuration only creates the Secret Manager **secret**. Add a secret version manually after running Terraform to avoid storing sensitive tokens in state:
>
> ```bash
> gcloud secrets versions add gmail-token --data-file=token.pickle --project=<YOUR_PROJECT_ID>
> ```

## Outputs

After `terraform apply`, useful values are printed:

- `service_account_email`: Email of the Cloud Function service account
- `pubsub_topic`: Pub/Sub topic receiving Gmail notifications
- `gmail_token_secret`: Secret Manager resource path for the Gmail token
- `function_name`: Name of the deployed Cloud Function
