provider "aws" {
  region = "us-east-1"
}

module "vpc" {
  source              = "../../modules/vpc"
  vpc_cidr            = var.vpc_cidr
  public_subnet_cidrs = var.public_subnet_cidrs
}

module "wallet_score_agent" {
  source             = "../../modules/agent_runtime"
  agent_name         = "wallet-score-agent"
  image_uri          = module.ecr_wallet_score_agent.repository_url
  cpu                = 256
  memory             = 512
  aws_region         = var.aws_region
  container_port     = 8000
  execution_role_arn = module.iam.execution_role_arn
  task_role_arn      = module.iam.task_role_arn
  log_group          = "/ecs/fortistk-agents"
  subnet_ids         = module.vpc.public_subnet_ids
  security_group_id  = var.agent_security_group_id
  target_group_arn   = module.alb_wallet_score_agent.target_group_arn
  cluster_id         = var.ecs_cluster_id
  desired_count      = 1
}

# ECR for agent image storage
module "ecr_wallet_score_agent" {
  source          = "../../modules/ecr"
  repository_name = "wallet-score-agent"
}

# IAM roles for ECS tasks
module "iam" {
  source = "../../modules/iam"
}

# ALB + Target Group for this agent
module "alb_wallet_score_agent" {
  source            = "../../modules/alb"
  alb_name          = "fortistk-alb"
  target_group_name = "fortistk-wallet-score"
  port              = 8000
  security_group_id = var.agent_security_group_id
  subnet_ids        = module.vpc.public_subnet_ids
  vpc_id            = module.vpc.vpc_id
}
