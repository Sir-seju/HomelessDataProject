
variable "environment_name" {
  type    = string
  default = "homeless-backend"
}

variable "instance_type" {
  type    = string
  default = "t3.micro"
}

variable "region" {
  type    = string
  default = "us-east-1"
}

variable "availability_zone" {
  type    = string
  default = "Any"
}

variable "environment_variables" {
  type = map(string)
  default = {
    "PORT" = "8080"
  }
}