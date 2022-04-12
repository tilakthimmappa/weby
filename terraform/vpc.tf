resource "aws_vpc" "ecs-vpc" {
  cidr_block = var.cidr
  tags = {
    "Name" = "ecs-vpc"
  }
}

