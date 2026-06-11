output "microsoft_graph_secret_arn" {
  description = "ARN of the Microsoft Graph Secrets Manager secret"
  value       = aws_secretsmanager_secret.microsoft_graph.arn
}

output "flight_api_secret_arn" {
  description = "ARN of the Flight API Secrets Manager secret"
  value       = aws_secretsmanager_secret.flight_api.arn
}

output "restaurant_api_secret_arn" {
  description = "ARN of the Restaurant API Secrets Manager secret"
  value       = aws_secretsmanager_secret.restaurant_api.arn
}

output "news_api_secret_arn" {
  description = "ARN of the News API Secrets Manager secret"
  value       = aws_secretsmanager_secret.news_api.arn
}
