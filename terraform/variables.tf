variable "aws_region" {
  description = "AWS region for AWS Academy Learner Lab."
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Name prefix for all created AWS resources."
  type        = string
  default     = "praxis-day06-pypiserver"
}

variable "vpc_cidr_block" {
  description = "CIDR block for the VPC."
  type        = string
  default     = "10.0.0.0/16"
}

variable "public_subnet_cidr_block" {
  description = "CIDR block for the public subnet."
  type        = string
  default     = "10.0.1.0/24"
}

variable "allowed_ssh_cidr_blocks" {
  description = "CIDR blocks that are allowed to connect via SSH."
  type        = list(string)
  default     = ["0.0.0.0/0"]
}

variable "pypiserver_port" {
  description = "TCP port for the pypiserver package registry."
  type        = number
  default     = 8080
}

variable "instance_type" {
  description = "EC2 instance type for pypiserver."
  type        = string
  default     = "t3.micro"
}

variable "ssh_public_key_path" {
  description = "Optional path to an SSH public key that will be added to the ubuntu user's authorized_keys via cloud-init."
  type        = string
  default     = ""
}

variable "cloud_init_path" {
  description = "Path to the cloud-init file, relative to the terraform/ folder."
  type        = string
  default     = "../cloud-init/pypiserver.yaml"

  validation {
    condition     = fileexists(var.cloud_init_path)
    error_message = "cloud_init_path must point to an existing cloud-init file."
  }
}
