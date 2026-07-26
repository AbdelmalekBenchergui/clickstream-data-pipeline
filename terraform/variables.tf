variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Deployment environment"
  type        = string
  default     = "dev"
}

variable "raw_bucket_name" {
  description = "Raw bucket name for clickstream events and Glue scripts/temp"
  type        = string
}

variable "silver_bucket_name" {
  description = "Silver bucket name for processed data"
  type        = string
}

variable "gold_bucket_name" {
  description = "Gold bucket name for aggregated data"
  type        = string
}

variable "s3_prefix" {
  description = "S3 prefix/path for raw events within the raw bucket"
  type        = string
  default     = "events"
}

variable "ami_id" {
  description = "Amazon Machine Image ID"
  type        = string
}

variable "instance_type" {
  description = "EC2 instance type"
  type        = string
  default     = "t3.micro"
}

variable "key_name" {
  description = "EC2 Key Pair"
  type        = string
}

variable "ssh_allowed_cidr" {
  description = "CIDR block allowed to SSH"
  type        = string
}

variable "instance_count" {
  type        = number
  default     = 1
  description = "Number of EC2 instances for the producer"
}

variable "glue_database" {
  description = "Glue Catalog Database name prefix"
  type        = string
  default     = "clickstream_db"
}

variable "glue_version" {
  type        = string
  default     = "4.0"
  description = "AWS Glue runtime version"
}

variable "glue_worker_type" {
  type        = string
  default     = "G.1X"
  description = "Glue worker type"
}

variable "glue_number_of_workers" {
  type        = number
  default     = 2
  description = "Number of Glue workers"
}

variable "producer_role_name" {
  description = "Base name for IAM role for the EC2 producer"
  type        = string
  default     = "clickstream-producer-role"
}

variable "glue_role_name" {
  description = "Base name for IAM role for AWS Glue"
  type        = string
  default     = "clickstream-glue-role"
}


