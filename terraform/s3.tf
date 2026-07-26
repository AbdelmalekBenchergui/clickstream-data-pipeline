resource "aws_s3_bucket" "raw" {
  bucket        = var.raw_bucket_name
  force_destroy = true

  tags = {
    Name        = "clickstream-raw-${var.environment}"
    Environment = var.environment
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "raw_encryption" {
  bucket = aws_s3_bucket.raw.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_versioning" "raw_versioning" {
  bucket = aws_s3_bucket.raw.id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_public_access_block" "raw_public_access_block" {
  bucket = aws_s3_bucket.raw.id

  block_public_acls       = true
  ignore_public_acls      = true
  block_public_policy     = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket" "silver" {
  bucket        = var.silver_bucket_name
  force_destroy = true

  tags = {
    Name        = "clickstream-silver-${var.environment}"
    Environment = var.environment
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "silver_encryption" {
  bucket = aws_s3_bucket.silver.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_versioning" "silver_versioning" {
  bucket = aws_s3_bucket.silver.id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_public_access_block" "silver_public_access_block" {
  bucket = aws_s3_bucket.silver.id

  block_public_acls       = true
  ignore_public_acls      = true
  block_public_policy     = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket" "gold" {
  bucket        = var.gold_bucket_name
  force_destroy = true

  tags = {
    Name        = "clickstream-gold-${var.environment}"
    Environment = var.environment
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "gold_encryption" {
  bucket = aws_s3_bucket.gold.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_versioning" "gold_versioning" {
  bucket = aws_s3_bucket.gold.id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_public_access_block" "gold_public_access_block" {
  bucket = aws_s3_bucket.gold.id

  block_public_acls       = true
  ignore_public_acls      = true
  block_public_policy     = true
  restrict_public_buckets = true
}

output "s3_raw_bucket_name" {
  value       = aws_s3_bucket.raw.id
  description = "S3 raw bucket name"
}

output "s3_silver_bucket_name" {
  value       = aws_s3_bucket.silver.id
  description = "S3 silver bucket name"
}

output "s3_gold_bucket_name" {
  value       = aws_s3_bucket.gold.id
  description = "S3 gold bucket name"
}

output "s3_raw_path" {
  value       = "s3://${aws_s3_bucket.raw.id}/clickstream-raw/"
  description = "S3 path for raw events"
}

output "s3_silver_path" {
  value       = "s3://${aws_s3_bucket.silver.id}/clickstream-silver/"
  description = "S3 path for silver data"
}

output "s3_gold_path" {
  value       = "s3://${aws_s3_bucket.gold.id}/clickstream-gold/"
  description = "S3 path for gold data"
}


