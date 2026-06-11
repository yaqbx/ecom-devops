output "terraform_github_role_arn" {
  value = aws_iam_role.terraform_github.arn
}

output "terraform_github_pr_role_arn" {
  value = aws_iam_role.terraform_github_pr.arn
}

output "app_build_role_arn" {
  value = aws_iam_role.app_build.arn
}