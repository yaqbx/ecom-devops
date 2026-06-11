locals {
  app_build_policy       = jsondecode(file("${path.root}/../iam/app-build-policy.json"))
  readonly_policy        = jsondecode(file("${path.root}/../iam/terraform-readonly-policy.json"))
  full_access_policy     = jsondecode(file("${path.root}/../iam/terraform-full-access-policy.json"))
  state_access_policy    = jsondecode(file("${path.root}/../iam/terraform-state-access-policy.json"))
  state_read_policy      = jsondecode(file("${path.root}/../iam/terraform-state-read-policy.json"))
}

resource "aws_iam_role" "terraform_github" {
  name               = "terraform-github-role"
  assume_role_policy = file("${path.root}/../iam/terraform-github-trust.json")
  tags               = var.tags
}

resource "aws_iam_role_policy" "terraform_github" {
  role   = aws_iam_role.terraform_github.name
  name   = "TerraformFullAccess"
  policy = jsonencode(local.full_access_policy)
}

resource "aws_iam_role_policy" "terraform_github_state" {
  role   = aws_iam_role.terraform_github.name
  name   = "TerraformStateAccess"
  policy = jsonencode(local.state_access_policy)
}

resource "aws_iam_role" "terraform_github_pr" {
  name               = "terraform-github-role-pr"
  assume_role_policy = file("${path.root}/../iam/terraform-github-pr-trust.json")
  tags               = var.tags
}

resource "aws_iam_role_policy" "terraform_github_pr" {
  role   = aws_iam_role.terraform_github_pr.name
  name   = "TerraformReadOnly"
  policy = jsonencode(local.readonly_policy)
}

resource "aws_iam_role_policy" "terraform_github_pr_state" {
  role   = aws_iam_role.terraform_github_pr.name
  name   = "TerraformStateRead"
  policy = jsonencode(local.state_read_policy)
}

resource "aws_iam_role" "app_build" {
  name               = "app-build-role"
  assume_role_policy = file("${path.root}/../iam/app-build-trust.json")
  tags               = var.tags
}

resource "aws_iam_role_policy" "app_build" {
  role   = aws_iam_role.app_build.name
  name   = "app-build-policy"
  policy = jsonencode(local.app_build_policy)
}