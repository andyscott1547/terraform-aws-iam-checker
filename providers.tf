# Providers

terraform {
  required_version = "~> 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.0"
    }
  }
}

provider "aws" {
  region = "eu-west-1"
  assume_role {
    role_arn = "arn:aws:iam::${local.acct_ids.mgmt}:role/TerraformRole"
  }
  # profile = "mgmt"
  default_tags {
    tags = local.tags
  }
}
