variable "REGION" {
  type = string
  default = "us-east-1"
}

variable "cidr" {
  type = string
  default = "10.0.0.0/16"
}

variable "azs" {
  type = list(string)
  default = [
      "us-east-1a",
      "us-east-1b"
  ]
}

variable "public-subnet-cidr" {
  type = list(string)
  default = [
    "10.0.0.0/24",
    "10.0.1.0/24"
  ]
}

variable "private-subnet-cidr" {
  type = string
  default = "10.0.2.24/24"  
}

variable "private-rds-subnet-cidr-1" {
  type = string
  default = "10.0.4.0/24"  
}

variable "az-1" {
  type = string
  default = "us-east-1a"
}

variable "private-rds-subnet-cidr_2" {
  type = string
  default = "10.0.5.0/24"  
}

variable "az-2" {
  type = string
  default = "us-east-1b"
}

variable "POSTGRES_DB" {
  type = string
  default = "weby"
}

variable "POSTGRES_USER" {
  type = string
  default = "postgres"
}

variable "POSTGRES_PASSWORD" {
  type = string
  default = "postgres"
}

data "aws_caller_identity" "current" {}

variable "ECR_REPO" {
  default = ""
}

variable "SECRET_KEY_BASE" {
  type = string
  default = "d42f89e05bca1a10b56952a91911aef765832ae23cb10c9af6729e3ddd3bed56cfadadd50353278890343719bfa3bbc319920573d3a3f812c32bd5b0d3fc6702"
}

variable "RAILS_ENV" {
  type = string
  default = "production"
}

variable "STORAGE_HOST" {
  type = string
  default = "s3.us-east-1.amazonaws.com"
}

variable "STORAGE_BUCKET" {
  type = string
  default = "weby-test"
}
