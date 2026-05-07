resource "aws_ecr_repository" "product_catalog" {
  name = "product-catalog"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = false
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
    scan_on_push = false
  }
  
  tags = var.tags
}

resource "aws_ecr_repository" "checkout_service" {
  name                 = "checkout-service"
  image_tag_mutability = "MUTABLE"
  
  image_scanning_configuration {
    scan_on_push = false
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
      "description": "Keep only 1 most recent image",
      "selection": {
        "tagStatus": "tagged",
        "tagPrefixList": ["latest"],
        "countType": "imageCountMoreThan",
        "countNumber": 1
      },
      "action": {
        "type": "expire"
      }
    },
    {
      "rulePriority": 2,
      "description": "Expire untagged images immediately",
      "selection": {
        "tagStatus": "untagged",
        "countType": "sinceImagePushed",
        "countNumber": 1,
        "countUnit": "days"
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
      "description": "Keep only 1 most recent image",
      "selection": {
        "tagStatus": "tagged",
        "tagPrefixList": ["latest"],
        "countType": "imageCountMoreThan",
        "countNumber": 1
      },
      "action": {
        "type": "expire"
      }
    },
    {
      "rulePriority": 2,
      "description": "Expire untagged images immediately",
      "selection": {
        "tagStatus": "untagged",
        "countType": "sinceImagePushed",
        "countNumber": 1,
        "countUnit": "days"
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
      "description": "Keep only 1 most recent image",
      "selection": {
        "tagStatus": "tagged",
        "tagPrefixList": ["latest"],
        "countType": "imageCountMoreThan",
        "countNumber": 1
      },
      "action": {
        "type": "expire"
      }
    },
    {
      "rulePriority": 2,
      "description": "Expire untagged images immediately",
      "selection": {
        "tagStatus": "untagged",
        "countType": "sinceImagePushed",
        "countNumber": 1,
        "countUnit": "days"
      },
      "action": {
        "type": "expire"
      }
    }
  ]
}
EOF
}