variable "alb_name" {}
variable "target_group_name" {}
variable "port" {
  default = 8000
}
variable "security_group_id" {}
variable "subnet_ids" {
  type = list(string)
}
variable "vpc_id" {}
