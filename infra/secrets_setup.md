# Secret Manager

The pipeline stores the Gmail OAuth token in Secret Manager so that Cloud Functions can access Gmail without bundling sensitive files in the deployment package.

## Steps

1. Enable the Secret Manager API:

   ```bash
   gcloud services enable secretmanager.googleapis.com --project=<YOUR_PROJECT_ID>
   ```

2. Create a secret and upload your `token.pickle`:

   ```bash
   gcloud secrets create gmail-token --replication-policy="automatic" --project=<YOUR_PROJECT_ID>
   gcloud secrets versions add gmail-token --data-file=token.pickle --project=<YOUR_PROJECT_ID>
   ```

3. Grant your Cloud Function service account access:

   ```bash
   gcloud projects add-iam-policy-binding <YOUR_PROJECT_ID> \
     --member="serviceAccount:gmail-function-sa@<YOUR_PROJECT_ID>.iam.gserviceaccount.com" \
     --role="roles/secretmanager.secretAccessor"
   ```

The function can then load the token using the Secret Manager API.
