terraform {
  backend "s3" {
    bucket = "terraform-state-pyconhk2023"
    key    = "terraform.tfstate"
    region = "ap-east-1"
  }
}
