
resource "aws_ecs_cluster" "imagestat" {
  name = "${local.ec2_resources_name}-cluster"
  tags = local.default_tags

  configuration {
    execute_command_configuration {
      kms_key_id = aws_kms_key.imagestat_kms_key.arn
      logging    = "OVERRIDE"

      log_configuration {
        cloud_watch_encryption_enabled = true
        cloud_watch_log_group_name     = aws_cloudwatch_log_group.imagestat_log_group.name
      }
    }
  }
}

resource "aws_kms_key" "imagestat_kms_key" {
  description             = "${local.ec2_resources_name}-kms-key"
  deletion_window_in_days = 7
  tags = local.default_tags
}

resource "aws_cloudwatch_log_group" "imagestat_log_group" {
  name = "${local.ec2_resources_name}-log-group"
  tags = local.default_tags
}

resource "aws_ecs_cluster_capacity_providers" "imagestat" {
  cluster_name = aws_ecs_cluster.imagestat.name
  capacity_providers = [aws_ecs_capacity_provider.imagestat.name]

  default_capacity_provider_strategy {
    base              = 1
    weight            = 100
    capacity_provider = aws_ecs_capacity_provider.imagestat.name
  }
}

resource "aws_ecs_capacity_provider" "imagestat" {
  name = "${local.ec2_resources_name}-capacity-provider"
  tags = local.default_tags

  auto_scaling_group_provider {
    auto_scaling_group_arn = aws_autoscaling_group.imagestat.arn
  }
}

resource "aws_autoscaling_group" "imagestat" {
  name = "${local.ec2_resources_name}-asg"

  max_size = 3
  min_size = 1

  vpc_zone_identifier = data.aws_subnets.private_application_subnets.ids

  launch_template {
    id = aws_launch_template.imagestat.id
    version = aws_launch_template.imagestat.latest_version
  }

  dynamic "tag" {
    for_each = local.default_tags

    content {
      key    =  tag.key
      value   =  tag.value
      propagate_at_launch =  true
    }
  }

}

data "template_file" "instance_user_data" {

  template = <<-EOT
    #!/bin/bash
    cat <<'EOF' >> /etc/ecs/ecs.config
    ECS_CLUSTER=${aws_ecs_cluster.imagestat.name}
    EOF
  EOT

}

resource "aws_launch_template" "imagestat" {
  name_prefix   = local.ec2_resources_name
  image_id      = data.aws_ssm_parameter.image_id_ecs_amz2.value
  instance_type = "t2.micro"
  user_data = base64encode(data.template_file.instance_user_data.rendered)

  iam_instance_profile {
    arn = aws_iam_instance_profile.imagestat.arn
  }
  vpc_security_group_ids = [aws_security_group.imagestat_alb.id]
  tags = local.default_tags

  tag_specifications {
    resource_type = "instance"

    tags = merge({
      Name = local.ec2_resources_name
    },
    local.default_tags)
  }
}


resource "aws_ecs_service" "gibs_imagestat" {
  name            = "${local.ec2_resources_name}-ecs-service"
  cluster         = aws_ecs_cluster.imagestat.id
  task_definition = aws_ecs_task_definition.imagestat.arn
  desired_count   = 1
  capacity_provider_strategy {
    capacity_provider = aws_ecs_capacity_provider.imagestat.name
    weight = 1
  }
  tags = local.default_tags

  network_configuration {
    subnets = data.aws_subnets.private_application_subnets.ids
    security_groups = [aws_security_group.imagestat_alb.id]
  }

  ordered_placement_strategy {
    type  = "binpack"
    field = "cpu"
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.imagestat.arn
    container_name   = local.container_name
    container_port   = 80
  }

  placement_constraints {
    type       = "memberOf"
    expression = "attribute:ecs.availability-zone in [us-west-2a, us-west-2b, us-west-2c]"
  }

  lifecycle {
    ignore_changes = [desired_count]
  }
}

resource "aws_ecs_task_definition" "imagestat" {
  family = local.ec2_resources_name
  execution_role_arn = aws_iam_role.imagestat_task_execution_role.arn
  task_role_arn = aws_iam_role.imagestat_task_role.arn
  network_mode = "awsvpc"
  tags = local.default_tags

  container_definitions = jsonencode([
    {
      name      = local.container_name
      image     = "${var.image_repository}/${var.image_name}:${var.image_tag}"
      cpu       = 10
      memory    = 512
      essential = true
      portMappings = [
        {
          containerPort = 80
          hostPort      = 80
        }
      ]
      logConfiguration: {
      logDriver: "awslogs",
      options: {
        awslogs-region: var.region,
        awslogs-group: aws_cloudwatch_log_group.imagestat_log_group.name,
        awslogs-stream-prefix: local.container_name
      }
    }
    }
  ])


  placement_constraints {
    type       = "memberOf"
    expression = "attribute:ecs.availability-zone in [us-west-2a, us-west-2b, us-west-2c]"
  }
}