# configure the S3 backend for storing state. This allows different
# team members to control and update terraform state.
terraform {
  backend "s3" {
    key    = "services/gibs-imagestat/terraform.tfstate"
    region = "us-west-2"
  }
}

provider "aws" {
  region = "us-west-2"

  ignore_tags {
    key_prefixes = ["gsfc-ngap"]
  }

  default_tags {
    tags = local.default_tags
  }
}

locals {
  name        = var.app_name
  environment = var.stage

  account_id = data.aws_caller_identity.current.account_id

  # This is the convention we use to know what belongs to each other
  ec2_resources_name = "svc-${local.name}-${local.environment}"

  container_name = "${local.ec2_resources_name}-task"

  default_tags = length(var.default_tags) == 0 ? {
    team: "TVA",
    application: local.ec2_resources_name,
    Environment = var.stage
    Version = var.image_tag
  } : var.default_tags
}

data "aws_caller_identity" "current" {}

data "aws_vpc" "application_vpc" {
  tags = {
    "Name": "Application VPC"
  }
}

data "aws_subnets" "private_application_subnets" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.application_vpc.id]
  }

  filter {
    name   = "tag:Name"
    values = ["Private application*"]
  }
}

data "aws_ssm_parameter" "image_id_ecs_amz2"{
  name = var.ecs_ami_id_ssm_name
}