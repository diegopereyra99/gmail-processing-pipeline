output "service_account_email" {
  description = "Email address of the Cloud Function service account."
  value       = google_service_account.function.email
}

output "pubsub_topic" {
  description = "Pub/Sub topic receiving Gmail push notifications."
  value       = google_pubsub_topic.gmail_watch.name
}

output "gmail_token_secret" {
  description = "Secret Manager resource name for the Gmail OAuth token."
  value       = google_secret_manager_secret.gmail_token.name
}

output "function_name" {
  description = "Deployed Cloud Function name."
  value       = google_cloudfunctions2_function.gmail_pubsub_trigger.name
}
