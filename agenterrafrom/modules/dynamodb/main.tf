resource "aws_dynamodb_table" "user_preferences" {
  name         = "user-preferences"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "user_id"

  attribute {
    name = "user_id"
    type = "S"
  }

  tags = {
    Name = "user-preferences"
  }
}
