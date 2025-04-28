variable "vpc_cidr" {
  type        = string
  description = "CIDR block for the VPC"
}

variable "public_subnet_cidrs" {
  type        = list(string)
  description = "CIDR blocks for public subnets"
}

variable "wallet_score_image_uri" {}
variable "agent_execution_role_arn" {}
variable "agent_task_role_arn" {}
variable "log_group" {}
variable "agent_security_group_id" {
  description = "Security group ID for agent tasks"
}
variable "agent_target_group_arn" {}
variable "ecs_cluster_id" {}
variable "aws_region" {
  default = "us-east-1"
}
