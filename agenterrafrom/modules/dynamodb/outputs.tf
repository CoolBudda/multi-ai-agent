output "table_name" {
  description = "Name of the DynamoDB user-preferences table"
  value       = aws_dynamodb_table.user_preferences.name
}

output "table_arn" {
  description = "ARN of the DynamoDB user-preferences table"
  value       = aws_dynamodb_table.user_preferences.arn
}
