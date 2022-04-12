# For ECS

resource "aws_security_group" "app-sg" {
  name = "weby"
  description = "Port 3000"
  vpc_id = aws_vpc.ecs-vpc.id

 ingress = [
   {
    cidr_blocks = [ "0.0.0.0/0" ]
    description = "Allow port 3000"
    protocol = "tcp"
    from_port = 3000
    to_port = 3000
    ipv6_cidr_blocks = []
    prefix_list_ids = []
    security_groups = []
    self = false
   }
  ]

  egress = [ {
    cidr_blocks = [ "0.0.0.0/0" ]
    description = "Allow all ip and ports outbound"
    protocol = "-1"
    from_port = 0
    to_port = 0
    ipv6_cidr_blocks = []
    prefix_list_ids = []
    security_groups = []
    self = false
  } ]
}

# For Application Load Balancer

resource "aws_security_group" "alb-sg" {
  name = "application-alb"
  description = "Port 80"
  vpc_id = aws_vpc.ecs-vpc.id

  ingress = [ {
    cidr_blocks = [ "0.0.0.0/0" ]
    description = "Allow Port 80"
    from_port = 80
    protocol = "tcp"
    to_port = 80
    ipv6_cidr_blocks = []
    prefix_list_ids = []
    security_groups = []
    self = false
  },
  {
    cidr_blocks = [ "0.0.0.0/0" ]
    description = "Allow Port 443"
    from_port = 443
    ipv6_cidr_blocks = [ ]
    protocol = "tcp"
    to_port = 443
    prefix_list_ids = []
    security_groups = []
    self = false
  } ]

  egress = [ {
    cidr_blocks = [ "0.0.0.0/0" ]
    description = "Allow all ip and ports outbound"
    protocol = "-1"
    from_port = 0
    to_port = 0
    ipv6_cidr_blocks = []
    prefix_list_ids = []
    security_groups = []
    self = false
  } ]
}

resource "aws_security_group" "rds-sg" {
  name = "rds-sg"
  description = "RDS postgres servers"
  vpc_id = aws_vpc.ecs-vpc.id

  ingress {
    from_port = 5432
    to_port = 5432
    protocol = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    ipv6_cidr_blocks = []
    prefix_list_ids = []
    security_groups = ["${aws_security_group.app-sg.id}"]
  }

  egress {
    from_port = 0
    to_port = 0
    protocol = "-1"
    cidr_blocks = ["0.0.0.0/0"]
    ipv6_cidr_blocks = []
    prefix_list_ids = []
    security_groups = []
  }
}