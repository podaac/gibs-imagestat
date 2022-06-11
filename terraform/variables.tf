variable "stage" {}

variable "image_tag" { default = "latest" }

variable "image_name" { default = "podaac/gibs-imagestat" }

variable "image_repository" { default = "ghcr.io" }

variable "region" {default = "us-west-2"}

variable "app_name" { default = "gibs-imagestat" }

variable "base_ami_id_ssm_name" {
  default = "image_id_amz2"
  description = "Name of the SSM Parameter that contains the NGAP approved non ECS AMI ID."
}

variable "ecs_ami_id_ssm_name" {
  default = "image_id_ecs_amz2"
  description = "Name of the SSM Parameter that contains the NGAP approved ECS AMI ID."
}

variable "default_tags" {
  type = map(string)
  default = {}
}

