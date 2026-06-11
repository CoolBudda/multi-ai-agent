resource "aws_secretsmanager_secret" "microsoft_graph" {
  name = "multi-ai-agent/microsoft-graph"
}

resource "aws_secretsmanager_secret_version" "microsoft_graph" {
  secret_id     = aws_secretsmanager_secret.microsoft_graph.id
  secret_string = "PLACEHOLDER"
}

resource "aws_secretsmanager_secret" "flight_api" {
  name = "multi-ai-agent/flight-api"
}

resource "aws_secretsmanager_secret_version" "flight_api" {
  secret_id     = aws_secretsmanager_secret.flight_api.id
  secret_string = "PLACEHOLDER"
}

resource "aws_secretsmanager_secret" "restaurant_api" {
  name = "multi-ai-agent/restaurant-api"
}

resource "aws_secretsmanager_secret_version" "restaurant_api" {
  secret_id     = aws_secretsmanager_secret.restaurant_api.id
  secret_string = "PLACEHOLDER"
}

resource "aws_secretsmanager_secret" "news_api" {
  name = "multi-ai-agent/news-api"
}

resource "aws_secretsmanager_secret_version" "news_api" {
  secret_id     = aws_secretsmanager_secret.news_api.id
  secret_string = "PLACEHOLDER"
}
