

# Public Subnets

resource "aws_subnet" "public-subnets" {
    count = length(var.azs)
    vpc_id = aws_vpc.ecs-vpc.id
    availability_zone = var.azs[count.index]
    cidr_block = var.public-subnet-cidr[count.index]
    map_public_ip_on_launch = true

    tags = {
      "Name" = "public-subnet"
    }
}

#Internet Gateway
resource "aws_internet_gateway" "i-gateway" {
    vpc_id = aws_vpc.ecs-vpc.id
    tags = {
      "Name" = "ecs-igtw"
    }
}

resource "aws_subnet" "private-rds-subnet-1" {
  cidr_block = var.private-rds-subnet-cidr-1
  vpc_id = aws_vpc.ecs-vpc.id
  availability_zone = var.az-1
  map_public_ip_on_launch = false

    tags = {
      "Name" = "private-rds-subnet-1"
    }
}

resource "aws_subnet" "private-rds-subnet-2" {
  cidr_block = var.private-rds-subnet-cidr_2
  vpc_id = aws_vpc.ecs-vpc.id
  availability_zone = var.az-2
  map_public_ip_on_launch = false

    tags = {
      "Name" = "private-rds-subnets-2"
    }
}