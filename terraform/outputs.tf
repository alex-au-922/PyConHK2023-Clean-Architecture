output "bastion_host_public_ipv4" {
  description = "Public IPv4 address of the Bastion Host"
  value       = aws_instance.bastion_host.public_ip
}
