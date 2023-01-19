# Locals

locals {
  acct_ids = {
    mgmt = "012345678910"       
  }

  tags = {
    Env        = terraform.workspace
    Project    = "project"
    Service    = "tf-iam-checker"
    Managed_By = "terraform"
  }

}
