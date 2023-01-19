# main.tf

module "lambda" {
  source              = "./modules/lambda"
  lambda_name         = "iam-checker"
  code_zip            = "my-deployment-package.zip"
  cloudwatch_schedule = "cron(0 6 * * ? *)"
  timeout             = 25
  custom_policy       = data.aws_iam_policy_document.iam_checker_policy.json
  additional_env_vars = {
    LOGGING_LEVEL = "INFO"
    MAX_KEY_AGE   = "90"
  }
}

resource "aws_ses_domain_identity" "this" {
  domain = var.domain_name
}

resource "aws_route53_record" "verification" {
  zone_id = data.aws_route53_zone.this.zone_id
  name    = "_amazonses.${aws_ses_domain_identity.this.id}"
  type    = "TXT"
  ttl     = "600"
  records = [aws_ses_domain_identity.this.verification_token]
}

resource "aws_ses_domain_identity_verification" "this" {
  domain = aws_ses_domain_identity.this.domain
  depends_on = [
    aws_route53_record.verification
  ]
}

resource "aws_ses_domain_dkim" "this" {
  domain = aws_ses_domain_identity.this.domain
  depends_on = [
    aws_ses_domain_identity_verification.this
  ]
}

resource "aws_route53_record" "dkim" {
  count   = 3
  zone_id = data.aws_route53_zone.this.zone_id
  name    = "${aws_ses_domain_dkim.this.dkim_tokens[count.index]}._domainkey"
  type    = "CNAME"
  ttl     = "600"
  records = ["${aws_ses_domain_dkim.this.dkim_tokens[count.index]}.dkim.amazonses.com"]
}

resource "aws_ses_domain_mail_from" "this" {
  domain           = aws_ses_domain_identity.this.domain
  mail_from_domain = "mail.${aws_ses_domain_identity.this.domain}"
}

resource "aws_route53_record" "mx" {
  zone_id = data.aws_route53_zone.this.zone_id
  name    = aws_ses_domain_mail_from.this.mail_from_domain
  type    = "MX"
  ttl     = "600"
  records = ["10 feedback-smtp.eu-west-1.amazonses.com"]
}

resource "aws_route53_record" "txt" {
  zone_id = data.aws_route53_zone.this.zone_id
  name    = aws_ses_domain_mail_from.this.mail_from_domain
  type    = "TXT"
  ttl     = "600"
  records = ["v=spf1 include:amazonses.com -all"]
}

resource "aws_ses_template" "iam_checker" {
  name    = "iam-checker-credential-alert"
  subject = "AWS Credential Alerts"
  html    = file("templates/email.html")
}