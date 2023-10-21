variable "vpc_config" {
  description = "Config for the VPC"
  type = object({
    name            = string
    cidr_block      = string
    private_subnets = list(string)
    public_subnets  = list(string)
  })
}
