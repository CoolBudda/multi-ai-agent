terraform {
  required_version = ">= 1.6.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

module "multi_ai_agent" {
  source = "../../"

  aws_region           = var.aws_region
  project_name         = "multi-ai-agent"
  vpc_cidr             = "10.0.0.0/16"
  public_subnet_cidrs  = ["10.0.1.0/24", "10.0.2.0/24"]
  private_subnet_cidrs = ["10.0.3.0/24", "10.0.4.0/24"]
  availability_zones   = ["us-east-1a", "us-east-1b"]
  cluster_name         = "multi-ai-agent-cluster"
  container_image      = var.container_image
  container_port       = 8000
  cpu                  = 1024
  memory               = 2048
  desired_count        = 2
  min_capacity         = 2
  max_capacity         = 4
  acm_certificate_arn  = var.acm_certificate_arn
}

variable "aws_region" {
  description = "AWS region for the dev environment"
  type        = string
  default     = "us-east-1"
}

variable "container_image" {
  description = "Container image URI for the ECS task definition"
  type        = string
}

variable "acm_certificate_arn" {
  description = "TBD"
  type        = string
}
