variable "project_id" {
  description = "Google Cloud project ID to deploy resources into."
  type        = string
}

variable "region" {
  description = "Region for regional resources such as Cloud Functions and storage."
  type        = string
  default     = "us-central1"
}

variable "sheet_id" {
  description = "Google Sheet ID used by the Gmail listener to store results."
  type        = string
}

variable "pubsub_topic" {
  description = "Name of the Pub/Sub topic Gmail will publish notifications to."
  type        = string
  default     = "gmail-watch"
}

variable "gmail_function_sa" {
  description = "ID (short name) for the Cloud Function service account."
  type        = string
  default     = "gmail-function-sa"
}

variable "gmail_token_secret_id" {
  description = "Secret Manager ID for the Gmail OAuth token."
  type        = string
  default     = "gmail-token"
}

variable "function_name" {
  description = "Cloud Function name for the Gmail Pub/Sub listener."
  type        = string
  default     = "gmail-pubsub-trigger"
}

variable "function_source_bucket" {
  description = "Optional override for the storage bucket used to stage the Cloud Function source."
  type        = string
  default     = ""
}
