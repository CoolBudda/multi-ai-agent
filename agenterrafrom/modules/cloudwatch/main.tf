resource "aws_cloudwatch_log_group" "ecs" {
  name = "/ecs/multi-ai-agent"
}

resource "aws_sns_topic" "alarms" {
  name = "${var.project_name}-alarms"
}
