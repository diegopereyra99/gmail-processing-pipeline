# Gmail Watch and Pub/Sub

Gmail can publish notifications to Google Pub/Sub when new messages arrive. This section describes how to configure that integration.

## 1. Create the Topic

```bash
gcloud pubsub topics create gmail-watch
```

## 2. Grant Gmail Permission

Gmail uses a special service account to publish messages. Grant it the publisher role on the topic:

```bash
gcloud pubsub topics add-iam-policy-binding gmail-watch \
  --member="serviceAccount:gmail-api-push@system.gserviceaccount.com" \
  --role="roles/pubsub.publisher"
```

## 3. Start the Watch

Use the helper script to register the watch on your inbox:

```bash
python gmail/start_watch.py
```

The script reads `token.pickle` and requests Gmail to publish updates to the topic specified inside the script.

⏰ **Watches expire every 7 days.** Re-run the script manually or automate it with Cloud Scheduler.

Once active, new emails trigger Pub/Sub messages that can invoke your Cloud Function.
