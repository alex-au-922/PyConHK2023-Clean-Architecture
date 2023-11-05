locals {
  allowed_cidrs = split(",", var.allowed_cidrs_string)
  tags = {
    developer = "alexau"
    contact   = "alexuau922@gmail.com"
  }
}
