# KMS key for encryption
resource "aws_kms_key" "main" {
  description             = "KMS key for encrypting logs and secrets"
  deletion_window_in_days = 7
  enable_key_rotation     = true

  tags = {
    Name        = "${var.project_name}-kms-key"
    Environment = var.environment
  }
}

resource "aws_kms_alias" "main" {
  name          = "alias/${var.project_name}-${var.environment}"
  target_key_id = aws_kms_key.main.key_id
}

# Secrets Manager for API keys and credentials
resource "aws_secretsmanager_secret" "api_keys" {
  name       = "${var.project_name}-${var.environment}-api-keys"
  kms_key_id = aws_kms_key.main.arn

  tags = {
    Name        = "${var.project_name}-api-keys"
    Environment = var.environment
  }
}

resource "aws_secretsmanager_secret_version" "api_keys" {
  secret_id = aws_secretsmanager_secret.api_keys.id
  secret_string = jsonencode({
    ETHERSCAN_API_KEY = var.etherscan_api_key
    OPENAI_API_KEY    = var.openai_api_key
    DATABASE_URL      = var.database_url
  })
}

# CloudWatch Log Group with KMS encryption
resource "aws_cloudwatch_log_group" "ecs_logs" {
  name              = "/ecs/${var.project_name}-${var.environment}"
  retention_in_days = 30
  kms_key_id        = aws_kms_key.main.arn

  tags = {
    Name        = "${var.project_name}-ecs-logs"
    Environment = var.environment
  }
}

# ECR Repository
resource "aws_ecr_repository" "wallet_score_agent" {
  name                 = "wallet-score-agent"
  image_tag_mutability = "MUTABLE"

  encryption_configuration {
    encryption_type = "KMS"
    kms_key         = aws_kms_key.main.arn
  }

  image_scanning_configuration {
    scan_on_push = true
  }

  tags = {
    Name        = "wallet-score-agent"
    Environment = var.environment
  }
}

# IAM Role for ECS Task Execution with specific ARNs
resource "aws_iam_role" "ecs_task_execution" {
  name = "${var.project_name}-${var.environment}-ecs-task-execution"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "ecs-tasks.amazonaws.com"
      }
    }]
  })

  tags = {
    Name        = "${var.project_name}-ecs-task-execution"
    Environment = var.environment
  }
}

# IAM Policy with specific resource ARNs
resource "aws_iam_role_policy" "ecs_task_execution" {
  name = "${var.project_name}-${var.environment}-ecs-execution-policy"
  role = aws_iam_role.ecs_task_execution.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "ecr:GetAuthorizationToken",
          "ecr:BatchCheckLayerAvailability",
          "ecr:GetDownloadUrlForLayer",
          "ecr:BatchGetImage"
        ]
        Resource = aws_ecr_repository.wallet_score_agent.arn
      },
      {
        Effect = "Allow"
        Action = "ecr:GetAuthorizationToken"
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "${aws_cloudwatch_log_group.ecs_logs.arn}:*"
      },
      {
        Effect = "Allow"
        Action = [
          "secretsmanager:GetSecretValue"
        ]
        Resource = aws_secretsmanager_secret.api_keys.arn
      },
      {
        Effect = "Allow"
        Action = [
          "kms:Decrypt",
          "kms:DescribeKey"
        ]
        Resource = aws_kms_key.main.arn
      }
    ]
  })
}

# ECS Task Definition with Secrets Manager integration
resource "aws_ecs_task_definition" "wallet_score_agent" {
  family                   = "${var.project_name}-wallet-score-agent"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "256"
  memory                   = "512"
  execution_role_arn       = aws_iam_role.ecs_task_execution.arn

  container_definitions = jsonencode([{
    name  = "wallet-score-agent"
    image = "${aws_ecr_repository.wallet_score_agent.repository_url}:latest"
    
    secrets = [
      {
        name      = "ETHERSCAN_API_KEY"
        valueFrom = "${aws_secretsmanager_secret.api_keys.arn}:ETHERSCAN_API_KEY::"
      },
      {
        name      = "OPENAI_API_KEY"
        valueFrom = "${aws_secretsmanager_secret.api_keys.arn}:OPENAI_API_KEY::"
      },
      {
        name      = "DATABASE_URL"
        valueFrom = "${aws_secretsmanager_secret.api_keys.arn}:DATABASE_URL::"
      }
    ]

    logConfiguration = {
      logDriver = "awslogs"
      options = {
        "awslogs-group"         = aws_cloudwatch_log_group.ecs_logs.name
        "awslogs-region"        = var.aws_region
        "awslogs-stream-prefix" = "wallet-score-agent"
      }
    }
  }])

  tags = {
    Name        = "${var.project_name}-wallet-score-agent"
    Environment = var.environment
  }
}
