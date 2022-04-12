# Table for public subnets
resource "aws_route_table" "pb-table" {
  vpc_id = aws_vpc.ecs-vpc.id
}

resource "aws_route" "pub-route" {
  route_table_id = aws_route_table.pb-table.id
  destination_cidr_block = "0.0.0.0/0"
  gateway_id = aws_internet_gateway.i-gateway.id
}

resource "aws_route_table_association" "as-pub" {
  count          = length(var.azs)
  route_table_id = aws_route_table.pb-table.id
  subnet_id = "${aws_subnet.public-subnets[count.index].id}"
}