variable "project_name" {
  description = "Project name used for resource naming"
  type        = string
}

variable "secret_arns" {
  description = "List of Secrets Manager ARNs the ECS task execution role may access"
  type        = list(string)
}

variable "dynamodb_table_arn" {
  description = "ARN of the DynamoDB table the ECS task role may access"
  type        = string
}
