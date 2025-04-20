resource "aws_ecs_task_definition" "agent" {
  family                   = var.agent_name
  cpu                      = var.cpu
  memory                   = var.memory
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  execution_role_arn       = var.execution_role_arn
  task_role_arn            = var.task_role_arn

  container_definitions = jsonencode([
    {
      name  = var.agent_name
      image = var.image_uri
      portMappings = [{
        containerPort = var.container_port
        protocol      = "tcp"
      }]
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          awslogs-region        = var.aws_region
          awslogs-group         = var.log_group
          awslogs-stream-prefix = var.agent_name
        }
      }
    }
  ])
}

resource "aws_ecs_service" "agent" {
  name          = var.agent_name
  cluster       = var.cluster_id
  launch_type   = "FARGATE"
  desired_count = var.desired_count

  task_definition = aws_ecs_task_definition.agent.arn

  network_configuration {
    subnets          = var.subnet_ids
    assign_public_ip = true
    security_groups  = [var.security_group_id]
  }

  load_balancer {
    target_group_arn = var.target_group_arn
    container_name   = var.agent_name
    container_port   = var.container_port
  }

  depends_on = [aws_ecs_task_definition.agent]
}
