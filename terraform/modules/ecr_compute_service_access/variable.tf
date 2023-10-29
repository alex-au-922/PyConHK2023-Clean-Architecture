variable "name" {
  description = "Name of the repository"
  type        = string
}

variable "image_mutable" {
  description = "Whether the image is mutable or not"
  type        = bool
  default     = false
}

variable "force_delete" {
  description = "Whether to force delete the repository or not"
  type        = bool
  default     = false
}

variable "scan_on_push" {
  description = "Whether to scan on push or not"
  type        = bool
  default     = false
}

variable "keep_images" {
  description = "Number of images to keep"
  type        = number
  default     = 10
}

