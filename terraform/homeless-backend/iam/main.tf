##########################
# PROVIDER CONFIGURATION
##########################

provider "aws" {
  region = "us-east-1"
  default_tags {
    tags = {
      Automation = "Terraform"
    }
  }
}

terraform {
  required_version = ">= 1.1.6"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 3.6"
    }
  }
}

##########################
# Defining locals
##########################


##########################
# TERRAFORM CONFIGURATION
##########################

terraform {
  backend "s3" {
    bucket         = "graystum-terraform-backend"
    key            = "network/iam"
    region         = "us-east-1"
    dynamodb_table = "terraform_state_lock"
    encrypt        = true
  }
}
