output "repository_urls" {
  description = "Map of repository names to their URLs"
  value = {
    product_catalog  = aws_ecr_repository.product_catalog.repository_url
    user_management = aws_ecr_repository.user_management.repository_url
    checkout_service = aws_ecr_repository.checkout_service.repository_url
  }
}
output "repository_arns" {
  description = "Map of repository names to their ARNs"
  value = {
    product_catalog  = aws_ecr_repository.product_catalog.arn
    user_management = aws_ecr_repository.user_management.arn
    checkout_service = aws_ecr_repository.checkout_service.arn
  }
}