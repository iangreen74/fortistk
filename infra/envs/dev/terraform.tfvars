vpc_cidr = "10.0.0.0/16"

public_subnet_cidrs = [
  "10.0.1.0/24",
  "10.0.2.0/24"
]

wallet_score_image_uri     = "418295677815.dkr.ecr.us-east-1.amazonaws.com/wallet-score-agent:latest"
agent_execution_role_arn   = "arn:aws:iam::418295677815:role/ecsTaskExecutionRole"
agent_task_role_arn        = "arn:aws:iam::418295677815:role/ecsTaskRole"
log_group                  = "/ecs/fortistk-agents"
agent_security_group_id    = "sg-0abc123456def7890"
agent_target_group_arn     = "arn:aws:elasticloadbalancing:us-east-1:418295677815:targetgroup/fortistk-wallet-score/abc123"
ecs_cluster_id             = "arn:aws:ecs:us-east-1:418295677815:cluster/fortistk-cluster"

agent_security_group_id = "sg-0abc123456def7890"
