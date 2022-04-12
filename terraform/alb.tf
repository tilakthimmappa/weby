resource "aws_lb" "app-lb" {
  name = "app-lb"
  internal = false
  load_balancer_type = "application"
  security_groups = [ aws_security_group.alb-sg.id ]
  subnets = [ "${aws_subnet.public-subnets[0].id}","${aws_subnet.public-subnets[1].id}"  ]
}

resource "aws_lb_target_group" "tg-group" {
  name = "tg-group"
  port = "80"
  protocol = "HTTP"
  vpc_id = aws_vpc.ecs-vpc.id
  target_type = "ip"
}

resource "aws_alb_listener" "lab-listener" {
  load_balancer_arn = aws_lb.app-lb.arn
  port = "80"
  protocol = "HTTP"

  default_action {
    type = "forward"
    target_group_arn = aws_lb_target_group.tg-group.arn
  }
}

