# data.tf

data "aws_route53_zone" "this" {
  name         = var.domain_name
  private_zone = false
}

data "aws_iam_policy_document" "iam_checker_policy" {
  //checkov:skip=CKV_AWS_107
  //checkov:skip=CKV_AWS_110
  statement {
    sid    = "IAMCheckerAllow"
    effect = "Allow"

    actions = [
      "IAM:AddUserToGroup",
      "IAM:DeleteAccessKey",
      "IAM:DeleteSSHPublicKey",
      "IAM:GetAccessKeyLastUsed",
      "IAM:GetGroup",
      "IAM:GetUser",
      "IAM:ListAccessKeys",
      "IAM:ListGroupsForUser",
      "IAM:ListGroups",
      "IAM:ListSSHPublicKeys",
      "IAM:ListUsers",
      "IAM:ListMFADevices",
      "IAM:ListVirtualMFADevices",
      "IAM:RemoveUserFromGroup",
      "IAM:UpdateAccessKey",
      "IAM:UpdateLoginProfile",
      "IAM:GetLoginProfile",
      "IAM:CreateLoginProfile"
    ]

    resources = [
      "*"
    ]
  }

  statement {
    sid    = "AllowSESsendemail"
    effect = "Allow"

    actions = [
      "SES:SendTemplatedEmail"
    ]

    resources = ["*"]
  }
}