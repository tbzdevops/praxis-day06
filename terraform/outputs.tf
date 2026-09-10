output "ec2_public_ip" {
  description = "Public IPv4 address of the EC2 instance."
  value       = aws_instance.pypiserver.public_ip
}

output "ec2_public_dns" {
  description = "Public DNS name of the EC2 instance."
  value       = aws_instance.pypiserver.public_dns
}

output "pypiserver_url" {
  description = "URL of the pypiserver web UI."
  value       = "http://${aws_instance.pypiserver.public_dns}:${var.pypiserver_port}"
}

output "pypiserver_upload_url" {
  description = "Repository URL for twine uploads."
  value       = "http://${aws_instance.pypiserver.public_dns}:${var.pypiserver_port}/"
}

output "pypiserver_index_url" {
  description = "Simple index URL for pip installs."
  value       = "http://${aws_instance.pypiserver.public_dns}:${var.pypiserver_port}/simple/"
}
