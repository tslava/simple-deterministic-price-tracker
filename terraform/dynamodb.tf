resource "aws_dynamodb_table" "price_history" {
  name         = "${var.project_name}-price-history"
  billing_mode = "PAY_PER_REQUEST"  # On-demand, free tier eligible

  hash_key  = "product_id"
  range_key = "timestamp"

  attribute {
    name = "product_id"
    type = "S"  # String
  }

  attribute {
    name = "timestamp"
    type = "S"  # String (ISO 8601 format)
  }

  # Free tier: 25GB storage, 25 RCU, 25 WCU
  # One write/read per day = well within limits

  tags = {
    Name = "Price Tracker History"
  }
}
