variable "agent_name" {}
variable "image_uri" {}
variable "cpu" {
  default = 256
}
variable "memory" {
  default = 512
}
variable "container_port" {
  default = 8000
}
variable "aws_region" {}
variable "execution_role_arn" {}
variable "task_role_arn" {}
variable "log_group" {}
variable "subnet_ids" {
  type = list(string)
}
variable "security_group_id" {}
variable "target_group_arn" {}
variable "cluster_id" {}
variable "desired_count" {
  default = 1
}
