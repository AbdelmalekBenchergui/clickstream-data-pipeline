resource "aws_iam_role" "producer_lambda" {
  name = "clickstream-producer-lambda-role-${var.environment}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
        Action = "sts:AssumeRole"
      }
    ]
  })

  tags = {
    Environment = var.environment
  }
}

resource "aws_iam_role_policy" "producer_lambda" {
  name = "clickstream-producer-lambda-policy-${var.environment}"
  role = aws_iam_role.producer_lambda.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "S3WriteAccess"
        Effect = "Allow"
        Action = [
          "s3:PutObject",
        ]
        Resource = [
          "${aws_s3_bucket.raw.arn}/${var.s3_prefix}/*"
        ]
      },
      {
        Sid    = "S3ListAccess"
        Effect = "Allow"
        Action = [
          "s3:ListBucket",
        ]
        Resource = [
          aws_s3_bucket.raw.arn,
        ]
      },
      {
        Sid    = "CloudWatchLogs"
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents",
        ]
        Resource = [
          "arn:aws:logs:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:log-group:/aws/lambda/clickstream-producer-${var.environment}:*"
        ]
      },
    ]
  })
}

resource "null_resource" "build_faker_layer" {
  triggers = {
    handler   = filemd5("${path.module}/../src/aws/lambda/producer_handler.py")
    event_gen = filemd5("${path.module}/../src/producer/event_generator.py")
    generate  = filemd5("${path.module}/../src/producer/generate.py")
    schema    = filemd5("${path.module}/../src/producer/modele_schema.py")
    uploader  = filemd5("${path.module}/../src/aws/s3/s3_uploader.py")
  }

  provisioner "local-exec" {
    command = <<EOT
      set -e
      LAYER_DIR=/tmp/faker-layer
      rm -rf $LAYER_DIR
      mkdir -p $LAYER_DIR/python
      pip install faker -t $LAYER_DIR/python -q
      cd $LAYER_DIR
      rm -f /tmp/faker-layer.zip
      zip -r /tmp/faker-layer.zip . -x "*.pyc" "__pycache__/*" "pip/_internal/*" > /dev/null 2>&1 || zip -r /tmp/faker-layer.zip .
    EOT
  }
}

resource "aws_lambda_layer_version" "faker" {
  filename            = "/tmp/faker-layer.zip"
  layer_name          = "faker-${var.environment}"
  compatible_runtimes = ["python3.9", "python3.10", "python3.11", "python3.12"]

  depends_on = [null_resource.build_faker_layer]
}

data "archive_file" "producer_lambda" {
  type        = "zip"
  output_path = "/tmp/clickstream-producer-lambda.zip"

  source {
    filename = "handler.py"
    content  = file("${path.module}/../src/aws/lambda/producer_handler.py")
  }

  source {
    filename = "src/producer/__init__.py"
    content  = file("${path.module}/../src/producer/__init__.py")
  }

  source {
    filename = "src/producer/event_generator.py"
    content  = file("${path.module}/../src/producer/event_generator.py")
  }

  source {
    filename = "src/producer/generate.py"
    content  = file("${path.module}/../src/producer/generate.py")
  }

  source {
    filename = "src/producer/modele_schema.py"
    content  = file("${path.module}/../src/producer/modele_schema.py")
  }

  source {
    filename = "src/aws/s3/__init__.py"
    content  = ""
  }

  source {
    filename = "src/aws/s3/s3_uploader.py"
    content  = file("${path.module}/../src/aws/s3/s3_uploader.py")
  }
}

resource "aws_lambda_function" "producer" {
  function_name    = "clickstream-producer-${var.environment}"
  filename         = data.archive_file.producer_lambda.output_path
  source_code_hash = data.archive_file.producer_lambda.output_base64sha256
  role             = aws_iam_role.producer_lambda.arn
  handler          = "handler.lambda_handler"
  runtime          = "python3.10"
  timeout          = 300
  memory_size      = 256
  layers           = [aws_lambda_layer_version.faker.arn]

  environment {
    variables = {
      S3_BUCKET = var.raw_bucket_name
      S3_PREFIX = var.s3_prefix
      NUM_USERS = "50"
    }
  }

  tags = {
    Name        = "clickstream-producer-${var.environment}"
    Environment = var.environment
  }

  depends_on = [aws_lambda_layer_version.faker]
}

output "producer_lambda_function_name" {
  value       = aws_lambda_function.producer.function_name
  description = "Producer Lambda function name"
}

output "producer_lambda_arn" {
  value       = aws_lambda_function.producer.arn
  description = "Producer Lambda function ARN"
}
