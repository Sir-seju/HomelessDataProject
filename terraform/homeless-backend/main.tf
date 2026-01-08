##########################
# Defining locals
##########################

locals {
  runtime          = "64bit Amazon Linux 2023 v4.3.2 running Python 3.12"
  vpc_id           = data.aws_vpc.vpc.id
  public_subnets   = [data.aws_subnet.pub-1.id, data.aws_subnet.pub-2.id, data.aws_subnet.pub-3.id]
  private_subnets   = [data.aws_subnet.priv-1.id, data.aws_subnet.priv-2.id, data.aws_subnet.priv-3.id]
  key_name         = data.aws_key_pair.lab.key_name
  instance_profile = data.aws_iam_instance_profile.eb-ec2-role.name
  service_name     = data.aws_iam_role.eb-ec2-service.arn
  app_name         = "HomelessDataBackend"
}


##########################
# TERRAFORM CONFIGURATION
##########################

terraform {
  backend "s3" {
    bucket         = "graystum-terraform-backend"
    key            = "beanstalk/homeless-backend"
    region         = "us-east-1"
    dynamodb_table = "terraform_state_lock"
    encrypt        = true
  }
}

######################################
# Data layer for Existing Resources
######################################

data "aws_vpc" "vpc" {
  filter {
    name   = "tag:Name"
    values = ["dev-homeless"]
  }
}

data "aws_subnet" "pub-1" {
  filter {
    name   = "tag:Name"
    values = ["public-a"]
  }
}

data "aws_subnet" "pub-2" {
  filter {
    name   = "tag:Name"
    values = ["public-b"]
  }
}

data "aws_subnet" "pub-3" {
  filter {
    name   = "tag:Name"
    values = ["public-c"]
  }
}

data "aws_subnet" "priv-1" {
  filter {
    name   = "tag:Name"
    values = ["private-a"]
  }
}

data "aws_subnet" "priv-2" {
  filter {
    name   = "tag:Name"
    values = ["private-b"]
  }
}

data "aws_subnet" "priv-3" {
  filter {
    name   = "tag:Name"
    values = ["private-c"]
  }
}

data "aws_iam_instance_profile" "eb-ec2-role" {
  name = "aws-instance-role-eb-ec2"
}

data "aws_iam_role" "eb-ec2-service" {
  name = "aws-role-eb-service"
}

data "aws_key_pair" "lab" {
  key_name = "dev"
}

##########################################
# Deploy elastic beanstalk applictaion 
##########################################

module "be-local" {
  source                = "../modules/elasticbeanstalk-alb"
  region                = var.region
  Application_name      = local.app_name
  availability_zone     = var.availability_zone
  environment_name      = var.environment_name
  vpc_id                = local.vpc_id
  loadbalancer_subnets  = local.public_subnets
  application_subnets   = local.private_subnets
  solution_stack_name   = local.runtime
  loadbalancer_type     = "application"
  service_role          = local.service_name
  instance_type         = var.instance_type
  instance_profile_role = local.instance_profile
  aws_key_pair          = local.key_name
  autoscale_max         = 3
  autoscale_min         = 1
  cooldown              = 900
  lower_threshold       = 20
  upper_threshold       = 50
  environment_url       = join("-", [local.app_name, var.environment_name])
}

