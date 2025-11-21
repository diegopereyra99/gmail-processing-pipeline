provider "google" {
  project = var.project_id
  region  = var.region
}

locals {
  required_services = [
    "aiplatform.googleapis.com",
    "cloudbuild.googleapis.com",
    "cloudfunctions.googleapis.com",
    "documentai.googleapis.com",
    "eventarc.googleapis.com",
    "gmail.googleapis.com",
    "iam.googleapis.com",
    "pubsub.googleapis.com",
    "run.googleapis.com",
    "secretmanager.googleapis.com",
    "sheets.googleapis.com",
    "storage.googleapis.com"
  ]

  function_bucket_name = var.function_source_bucket != "" ? var.function_source_bucket : "${var.project_id}-gmail-functions"
  function_sa_roles    = [
    "roles/aiplatform.user",
    "roles/cloudfunctions.invoker",
    "roles/documentai.apiUser",
    "roles/pubsub.publisher",
    "roles/secretmanager.secretAccessor",
    "roles/storage.objectAdmin"
  ]
}

resource "google_project_service" "services" {
  for_each                   = toset(local.required_services)
  service                    = each.key
  disable_dependent_services = true
  disable_on_destroy         = false
}

resource "google_service_account" "function" {
  account_id   = var.gmail_function_sa
  display_name = "Service account for Gmail PDF Processing"
  depends_on   = [google_project_service.services["iam.googleapis.com"]]
}

resource "google_project_iam_member" "function_roles" {
  for_each = toset(local.function_sa_roles)

  project = var.project_id
  role    = each.key
  member  = "serviceAccount:${google_service_account.function.email}"
}

resource "google_pubsub_topic" "gmail_watch" {
  name       = var.pubsub_topic
  depends_on = [google_project_service.services["pubsub.googleapis.com"]]
}

resource "google_pubsub_topic_iam_member" "gmail_api_publisher" {
  topic  = google_pubsub_topic.gmail_watch.name
  role   = "roles/pubsub.publisher"
  member = "serviceAccount:gmail-api-push@system.gserviceaccount.com"
}

resource "google_secret_manager_secret" "gmail_token" {
  secret_id = var.gmail_token_secret_id
  replication {
    auto {}
  }
  depends_on = [google_project_service.services["secretmanager.googleapis.com"]]
}

resource "google_secret_manager_secret_iam_member" "function_access" {
  secret_id = google_secret_manager_secret.gmail_token.id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.function.email}"
}

resource "google_storage_bucket" "function_source" {
  name                        = local.function_bucket_name
  location                    = var.region
  uniform_bucket_level_access = true
  force_destroy               = true

  depends_on = [google_project_service.services["storage.googleapis.com"]]
}

data "archive_file" "gmail_listener" {
  type        = "zip"
  source_dir  = "${path.module}/../../functions/gmail_listener"
  output_path = "${path.module}/build/gmail_listener.zip"
}

resource "google_storage_bucket_object" "function_archive" {
  name   = "gmail_listener.zip"
  bucket = google_storage_bucket.function_source.name
  source = data.archive_file.gmail_listener.output_path

  content_type = "application/zip"
}

resource "google_cloudfunctions2_function" "gmail_pubsub_trigger" {
  name     = var.function_name
  location = var.region

  build_config {
    runtime     = "python310"
    entry_point = "gmail_pubsub_trigger"

    source {
      storage_source {
        bucket = google_storage_bucket.function_source.name
        object = google_storage_bucket_object.function_archive.name
      }
    }
  }

  service_config {
    available_memory      = "512M"
    timeout_seconds       = 60
    service_account_email = google_service_account.function.email

    environment_variables = {
      SHEET_ID   = var.sheet_id
      PROJECT_ID = var.project_id
    }
  }

  event_trigger {
    event_type   = "google.cloud.pubsub.topic.v1.messagePublished"
    pubsub_topic = google_pubsub_topic.gmail_watch.id
    retry_policy = "RETRY_POLICY_RETRY"
    trigger_region = var.region
  }

  depends_on = [
    google_project_service.services["cloudfunctions.googleapis.com"],
    google_project_service.services["eventarc.googleapis.com"],
    google_project_service.services["pubsub.googleapis.com"],
    google_project_service.services["run.googleapis.com"],
    google_project_service.services["cloudbuild.googleapis.com"]
  ]
}
