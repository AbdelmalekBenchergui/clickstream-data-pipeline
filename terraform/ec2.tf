resource "aws_security_group" "producer" {
  name        = "clickstream-producer-${var.environment}-sg"
  description = "Allow SSH to producer and all outbound traffic"

  ingress {
    description = "SSH"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = [var.ssh_allowed_cidr]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name        = "clickstream-producer-${var.environment}"
    Environment = var.environment
  }
}

resource "aws_instance" "producer" {
  ami                         = var.ami_id
  instance_type               = var.instance_type
  key_name                    = var.key_name
  iam_instance_profile        = aws_iam_instance_profile.producer_profile.name
  associate_public_ip_address = true
  vpc_security_group_ids      = [aws_security_group.producer.id]

  user_data = base64encode(templatefile("${path.module}/user_data.sh", {
    S3_BUCKET      = aws_s3_bucket.raw.bucket
    S3_PREFIX      = "events"
    NUM_USERS      = 50
    EVENTS_PER_SEC = 15
    REPO_DIR       = "/home/ec2-user/clickstream-lakehouse"
  }))

  tags = {
    Name        = "clickstream-producer-${var.environment}-instance"
    Environment = var.environment
  }

  depends_on = [
    aws_iam_instance_profile.producer_profile,
    aws_s3_bucket.raw,
    aws_s3_object.producer_bundle,
  ]
}

resource "aws_s3_object" "producer_bundle" {
  bucket = aws_s3_bucket.raw.bucket
  key    = "clickstream-raw/producer-bundle.zip"
  source = "/tmp/clickstream-producer.zip"
  etag   = filemd5("/tmp/clickstream-producer.zip")
}

output "producer_instance_id" {
  value       = aws_instance.producer.id
  description = "ID of the EC2 producer instance"
}

output "producer_public_ip" {
  value       = aws_instance.producer.public_ip
  description = "Public IP address of the EC2 producer instance"
}
