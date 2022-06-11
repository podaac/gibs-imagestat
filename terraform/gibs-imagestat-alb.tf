
resource "aws_security_group" "imagestat_alb" {
  name_prefix = local.ec2_resources_name
  vpc_id = data.aws_vpc.application_vpc.id

  ingress {
    description      = "Allow HTTP traffic from self and VPC"
    from_port        = 80
    to_port          = 80
    protocol         = "tcp"
    cidr_blocks      = [data.aws_vpc.application_vpc.cidr_block]
    self = true
  }

  egress {
    from_port        = 0
    to_port          = 0
    protocol         = "-1"
    cidr_blocks      = ["0.0.0.0/0"]
    ipv6_cidr_blocks = ["::/0"]
  }

  tags = local.default_tags
}

resource "aws_lb" "imagestat" {
  name = local.ec2_resources_name
  internal = true
  security_groups = [aws_security_group.imagestat_alb.id]
  subnets = data.aws_subnets.private_application_subnets.ids
  enable_deletion_protection = true

  tags = local.default_tags
}

resource "aws_lb_target_group" "imagestat" {
  name = local.ec2_resources_name
  vpc_id = data.aws_vpc.application_vpc.id
  port = 80
  target_type = "ip"
  protocol = "HTTP"
}

resource "aws_alb_listener" "imagestat" {
  load_balancer_arn = aws_lb.imagestat.arn
  port              = "80"
  protocol = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.imagestat.arn
  }
}