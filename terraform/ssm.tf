# Free tier: Standard parameters are always free

resource "aws_ssm_parameter" "product_url" {
  name  = "/${var.project_name}/product-url"
  type  = "String"
  value = var.product_url

  tags = {
    Name = "Product URL"
  }
}

resource "aws_ssm_parameter" "price_selector" {
  name  = "/${var.project_name}/price-selector"
  type  = "String"
  value = var.price_selector

  tags = {
    Name = "Price CSS Selector"
  }
}

resource "aws_ssm_parameter" "telegram_bot_token" {
  name  = "/${var.project_name}/telegram-bot-token"
  type  = "SecureString"  # Encrypted at rest
  value = var.telegram_bot_token

  tags = {
    Name = "Telegram Bot Token"
  }
}

resource "aws_ssm_parameter" "telegram_chat_id" {
  name  = "/${var.project_name}/telegram-chat-id"
  type  = "SecureString"
  value = var.telegram_chat_id

  tags = {
    Name = "Telegram Chat ID"
  }
}
