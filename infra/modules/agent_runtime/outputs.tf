output "service_name" {
  value = aws_ecs_service.agent.name
}

output "task_def_arn" {
  value = aws_ecs_task_definition.agent.arn
}
