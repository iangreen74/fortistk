terraform {
  backend "s3" {
    bucket         = "fortistk-tfstate-us-east-1"
    key            = "dev/terraform.tfstate"
    region         = "us-east-1"
    dynamodb_table = "fortistk-tf-locks"
    encrypt        = true
  }
}
