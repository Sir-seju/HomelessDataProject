provider "aws" {
  region = "us-east-1"
}


resource "aws_dynamodb_table" "dynamodb-terraform-lock" {
  name           = "terraform_state_lock"
  hash_key       = "LockID"
  read_capacity  = 5
  write_capacity = 5

  attribute {
    name = "LockID"
    type = "S"
  }

  tags = {
    Name       = "Terraform Lock Table"
    Automation = "Terraform"
  }
}