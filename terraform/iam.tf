resource "aws_iam_role" "producer_role" {
  name = "${var.producer_role_name}-${var.environment}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ec2.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy" "producer_s3_policy" {
  name = "${var.producer_role_name}-${var.environment}-s3-policy"
  role = aws_iam_role.producer_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:PutObject",
          "s3:GetObject"
        ]
        Resource = "arn:aws:s3:::${aws_s3_bucket.raw.id}/events/*"
      },
      {
        Effect = "Allow"
        Action = [
          "s3:ListBucket"
        ]
        Resource = "arn:aws:s3:::${aws_s3_bucket.raw.id}"
      }
    ]
  })
}

resource "aws_iam_instance_profile" "producer_profile" {
  name = "${var.producer_role_name}-${var.environment}-profile"
  role = aws_iam_role.producer_role.name
}

resource "aws_iam_role" "glue_role" {
  name = "${var.glue_role_name}-${var.environment}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "glue.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy" "glue_policy" {
  name = "${var.glue_role_name}-${var.environment}-policy"
  role = aws_iam_role.glue_role.id

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:ListBucket",
          "s3:GetBucketLocation"
        ],
        Resource = [

          "arn:aws:s3:::${aws_s3_bucket.raw.id}",
          "arn:aws:s3:::${aws_s3_bucket.raw.id}/*",

          "arn:aws:s3:::${aws_s3_bucket.silver.id}",
          "arn:aws:s3:::${aws_s3_bucket.silver.id}/*",

          "arn:aws:s3:::${aws_s3_bucket.gold.id}",
          "arn:aws:s3:::${aws_s3_bucket.gold.id}/*"
        ]
      },
      {
        Effect = "Allow",
        Action = [
          "glue:*",
          "iam:PassRole",
          "ec2:CreateNetworkInterface",
          "ec2:DeleteNetworkInterface",
          "ec2:DescribeNetworkInterfaces",

          "glue:CreateCrawler",
          "glue:StartCrawler",
          "glue:GetCrawler",
          "glue:UpdateCrawler",
          "glue:DeleteCrawler"
        ],
        Resource = "*"
      },
      {
        Effect = "Allow",
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ],
        Resource = "arn:aws:logs:*:*:*"
      }
    ]
  })
}

output "producer_role_arn" {
  value       = aws_iam_role.producer_role.arn
  description = "ARN of the IAM role for the EC2 producer"
}

output "glue_role_arn" {
  value       = aws_iam_role.glue_role.arn
  description = "ARN of the IAM role for AWS Glue"
}
