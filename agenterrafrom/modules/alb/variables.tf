variable "project_name" {
  description = "Project name used for resource naming"
  type        = string
}

variable "vpc_id" {
  description = "ID of the VPC"
  type        = string
}

variable "public_subnet_ids" {
  description = "IDs of the public subnets for the ALB"
  type        = list(string)
}

variable "container_port" {
  description = "Port the container listens on (used for the target group)"
  type        = number
  default     = 8000
}

variable "acm_certificate_arn" {
  description = "TBD"
  type        = string
}
