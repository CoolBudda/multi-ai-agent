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

module "vpc" {
  source               = "./modules/vpc"
  project_name         = var.project_name
  vpc_cidr             = var.vpc_cidr
  public_subnet_cidrs  = var.public_subnet_cidrs
  private_subnet_cidrs = var.private_subnet_cidrs
  availability_zones   = var.availability_zones
}

module "dynamodb" {
  source = "./modules/dynamodb"
}

module "secrets" {
  source = "./modules/secrets"
}

module "cloudwatch" {
  source       = "./modules/cloudwatch"
  project_name = var.project_name
}

module "iam" {
  source = "./modules/iam"

  project_name = var.project_name
  secret_arns = [
    module.secrets.microsoft_graph_secret_arn,
    module.secrets.flight_api_secret_arn,
    module.secrets.restaurant_api_secret_arn,
    module.secrets.news_api_secret_arn,
  ]
  dynamodb_table_arn = module.dynamodb.table_arn
}

module "alb" {
  source = "./modules/alb"

  project_name        = var.project_name
  vpc_id              = module.vpc.vpc_id
  public_subnet_ids   = module.vpc.public_subnet_ids
  container_port      = var.container_port
  acm_certificate_arn = var.acm_certificate_arn
}

module "ecs" {
  source = "./modules/ecs"

  project_name            = var.project_name
  cluster_name            = var.cluster_name
  container_image         = var.container_image
  container_port          = var.container_port
  cpu                     = var.cpu
  memory                  = var.memory
  desired_count           = var.desired_count
  min_capacity            = var.min_capacity
  max_capacity            = var.max_capacity
  task_execution_role_arn = module.iam.task_execution_role_arn
  task_role_arn           = module.iam.task_role_arn
  private_subnet_ids      = module.vpc.private_subnet_ids
  vpc_id                  = module.vpc.vpc_id
  alb_security_group_id   = module.alb.security_group_id
  target_group_arn        = module.alb.target_group_arn
  log_group_name          = module.cloudwatch.log_group_name
  aws_region              = var.aws_region
}
