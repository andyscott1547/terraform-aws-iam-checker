resource "aws_iam_role" "this" {
  name = "${var.lambda_name}-${terraform.workspace}"

  assume_role_policy = data.aws_iam_policy_document.assumerole.json

  tags = merge(
    {
      "Name" = "${var.lambda_name}-${terraform.workspace}",
    },
  )
}

resource "aws_iam_role_policy_attachment" "role-policy-attachment-default" {
  for_each   = toset(concat(local.default_iam_policies, var.managed_policies))
  role       = aws_iam_role.this.name
  policy_arn = each.value
}

resource "aws_iam_role_policy" "role-policy-attachment-managed" {
  count  = var.custom_policy == "" ? 0 : 1
  name   = "${var.lambda_name}-custom-policy"
  role   = aws_iam_role.this.name
  policy = var.custom_policy
}
