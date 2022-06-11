# IAM definitions
resource "aws_iam_instance_profile" "imagestat" {
  name = "${local.ec2_resources_name}-instance-profile"
  role = aws_iam_role.imagestat_instance_role.name
  tags = local.default_tags
}

resource "aws_iam_role" "imagestat_instance_role" {
  name_prefix          = local.ec2_resources_name
  permissions_boundary = "arn:aws:iam::${local.account_id}:policy/NGAPShRoleBoundary"

  managed_policy_arns = [
    "arn:aws:iam::${local.account_id}:policy/NGAPProtAppInstanceMinimalPolicy"
  ]

  assume_role_policy = jsonencode(
    {
      "Version" : "2012-10-17",
      "Statement" : [
        {
          "Action" : "sts:AssumeRole",
          "Principal" : {
            "Service" : "ec2.amazonaws.com"
          },
          "Effect" : "Allow",
          "Sid" : ""
        }
      ]
    }
  )
  tags = local.default_tags
}

resource "aws_iam_role" "imagestat_task_role" {
  name_prefix = local.ec2_resources_name
  tags        = local.default_tags

  permissions_boundary = "arn:aws:iam::${local.account_id}:policy/NGAPShRoleBoundary"

  assume_role_policy = jsonencode({
    "Version" : "2012-10-17",
    "Statement" : [
      {
        "Sid" : "",
        "Effect" : "Allow",
        "Principal" : {
          "Service" : "ecs-tasks.amazonaws.com"
        },
        "Action" : "sts:AssumeRole"
        "Condition" : {
          "ArnLike" : {
            "aws:SourceArn" : "arn:aws:ecs:${var.region}:${local.account_id}:*"
          },
          "StringEquals" : {
            "aws:SourceAccount" : local.account_id
          }
        }
      }
    ]
  })

}

resource "aws_iam_role" "imagestat_task_execution_role" {
  name_prefix = local.ec2_resources_name
  tags        = local.default_tags

  permissions_boundary = "arn:aws:iam::${local.account_id}:policy/NGAPShRoleBoundary"

  managed_policy_arns = [
    "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
  ]

  inline_policy {
    policy = jsonencode({
      "Version" : "2012-10-17",
      "Statement" : [
        {
          "Effect" : "Allow",
          "Action" : [
            "logs:CreateLogStream",
            "logs:PutLogEvents"
          ],
          "Resource" : "*"
        }
      ]
    })
  }

  assume_role_policy = jsonencode({
    "Version" : "2012-10-17",
    "Statement" : [
      {
        "Sid" : "",
        "Effect" : "Allow",
        "Principal" : {
          "Service" : "ecs-tasks.amazonaws.com"
        },
        "Action" : "sts:AssumeRole"
      }
    ]
  })

}
