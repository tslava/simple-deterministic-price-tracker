resource "aws_ecr_repository" "price_tracker" {
  name                 = var.service_name
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  # Free tier: 500MB storage/month
  # Expected image size: ~1.5-2GB (requires cleanup of old images)

  tags = {
    Name = "Price Tracker Lambda Container"
  }
}

# Lifecycle policy to keep only latest 2 images (stay under 500MB)
resource "aws_ecr_lifecycle_policy" "price_tracker" {
  repository = aws_ecr_repository.price_tracker.name

  policy = jsonencode({
    rules = [{
      rulePriority = 1
      description  = "Keep only 2 most recent images"
      selection = {
        tagStatus   = "any"
        countType   = "imageCountMoreThan"
        countNumber = 2
      }
      action = {
        type = "expire"
      }
    }]
  })
}
