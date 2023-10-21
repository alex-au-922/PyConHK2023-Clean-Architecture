variable "name" {
  description = "Name of the secret"
  type        = string
}

variable "description" {
  description = "Description of the secret"
  type        = string
}

variable "recovery_window_in_days" {
  description = "The number of days that Secrets Manager waits before Secrets Manager can delete the secret"
  type        = number
  default     = 7
}

variable "secret_string" {
  description = "The plaintext data for the secret"
  type        = string
}
