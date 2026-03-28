# Main Terraform Configuration

terraform {
  required_version = ">= 1.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  backend "s3" {
    bucket         = "wallet-score-terraform-state"
    key            = "infrastructure/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "wallet-score-terraform-locks"
  }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = "wallet-score"
      Environment = var.environment
      ManagedBy   = "terraform"
    }
  }
}

variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "production"
}

# VPC Module
module "vpc" {
  source = "./modules/vpc"

  vpc_cidr     = "10.0.0.0/16"
  environment  = var.environment
  project_name = "wallet-score"
}

# Security Group for Agent Runtime
resource "aws_security_group" "agent_runtime" {
  name_prefix = "wallet-score-${var.environment}-agent-runtime-"
  description = "Security group for agent runtime in private subnets"
  vpc_id      = module.vpc.vpc_id

  ingress {
    description = "Allow internal VPC traffic"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["10.0.0.0/16"]
  }

  egress {
    description = "Allow all outbound traffic"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name        = "wallet-score-${var.environment}-agent-runtime-sg"
    Environment = var.environment
  }

  lifecycle {
    create_before_destroy = true
  }
}

# ECS Cluster for Agent Runtime
resource "aws_ecs_cluster" "agent_runtime" {
  name = "wallet-score-${var.environment}-agents"

  setting {
    name  = "containerInsights"
    value = "enabled"
  }

  tags = {
    Name        = "wallet-score-${var.environment}-agents"
    Environment = var.environment
  }
}

# IAM Role for ECS Task Execution
resource "aws_iam_role" "ecs_task_execution" {
  name = "wallet-score-${var.environment}-ecs-task-execution"

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
}

resource "aws_iam_role_policy_attachment" "ecs_task_execution" {
  role       = aws_iam_role.ecs_task_execution.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

# ECS Task Definition for Agent Runtime (using private subnets)
resource "aws_ecs_task_definition" "agent_runtime" {
  family                   = "wallet-score-${var.environment}-agent-runtime"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "256"
  memory                   = "512"
  execution_role_arn       = aws_iam_role.ecs_task_execution.arn

  container_definitions = jsonencode([{
    name  = "agent-runtime"
    image = "wallet-score-agent:latest"
    portMappings = [{
      containerPort = 8000
      protocol      = "tcp"
    }]
    logConfiguration = {
      logDriver = "awslogs"
      options = {
        "awslogs-group"         = "/ecs/wallet-score-${var.environment}-agent-runtime"
        "awslogs-region"        = var.aws_region
        "awslogs-stream-prefix" = "ecs"
      }
    }
  }])
}

# CloudWatch Log Group for ECS
resource "aws_cloudwatch_log_group" "ecs_agent_runtime" {
  name              = "/ecs/wallet-score-${var.environment}-agent-runtime"
  retention_in_days = 30

  tags = {
    Name        = "wallet-score-${var.environment}-agent-runtime-logs"
    Environment = var.environment
  }
}

# ECS Service (configured to use private subnets)
resource "aws_ecs_service" "agent_runtime" {
  name            = "wallet-score-${var.environment}-agent-runtime"
  cluster         = aws_ecs_cluster.agent_runtime.id
  task_definition = aws_ecs_task_definition.agent_runtime.arn
  desired_count   = 2
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = module.vpc.private_subnet_ids
    security_groups  = [aws_security_group.agent_runtime.id]
    assign_public_ip = false
  }

  tags = {
    Name        = "wallet-score-${var.environment}-agent-runtime"
    Environment = var.environment
  }
}

# Outputs
output "vpc_id" {
  value = module.vpc.vpc_id
}

output "private_subnet_ids" {
  value = module.vpc.private_subnet_ids
}

output "agent_runtime_security_group_id" {
  value = aws_security_group.agent_runtime.id
}

output "ecs_cluster_name" {
  value = aws_ecs_cluster.agent_runtime.name
}
