resource "aws_ecr_repository" "product_catalog" {
  name                 = "product-catalog"
  image_tag_mutability = "MUTABLE"
  
  image_scanning_configuration {
    scan_on_push = true
  }
  
  encryption_configuration {
    encryption_type = "AES256"
  }
  
  tags = var.tags
}
resource "aws_ecr_repository" "user_management" {
  name                 = "user-management"
  image_tag_mutability = "MUTABLE"
  
  image_scanning_configuration {
    scan_on_push = true
  }
  
  tags = var.tags
}
resource "aws_ecr_repository" "checkout_service" {
  name                 = "checkout-service"
  image_tag_mutability = "MUTABLE"
  
  image_scanning_configuration {
    scan_on_push = true
  }
  
  tags = var.tags
}
resource "aws_ecr_lifecycle_policy" "product_catalog" {
  repository = aws_ecr_repository.product_catalog.name
  
  policy = <<EOF
{
  "rules": [
    {
      "rulePriority": 1,
      "description": "Expire untagged images older than 14 days",
      "selection": {
        "tagStatus": "untagged",
        "countType": "sinceImagePushed",
        "countNumber": 14
      },
      "action": {
        "type": "expire"
      }
    }
  ]
}
EOF
}
resource "aws_ecr_lifecycle_policy" "user_management" {
  repository = aws_ecr_repository.user_management.name
  
  policy = <<EOF
{
  "rules": [
    {
      "rulePriority": 1,
      "description": "Expire untagged images older than 14 days",
      "selection": {
        "tagStatus": "untagged",
        "countType": "sinceImagePushed",
        "countNumber": 14
      },
      "action": {
        "type": "expire"
      }
    }
  ]
}
EOF
}
resource "aws_ecr_lifecycle_policy" "checkout_service" {
  repository = aws_ecr_repository.checkout_service.name
  
  policy = <<EOF
{
  "rules": [
    {
      "rulePriority": 1,
      "description": "Expire untagged images older than 14 days",
      "selection": {
        "tagStatus": "untagged",
        "countType": "sinceImagePushed",
        "countNumber": 14
      },
      "action": {
        "type": "expire"
      }
    }
  ]
}
EOF
}