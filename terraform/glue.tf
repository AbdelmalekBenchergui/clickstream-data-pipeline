resource "aws_glue_catalog_database" "clickstream_db" {
  name = "${var.glue_database}-${var.environment}"
}

resource "aws_s3_object" "glue_script" {
  bucket = aws_s3_bucket.raw.id

  key = "glue-scripts/clickstream_glue_job.py"

  source = "${path.module}/../src/aws/glue/glue_job_silver.py"

  etag = filemd5("${path.module}/../src/aws/glue/glue_job_silver.py")
}

resource "aws_s3_object" "gold_script" {
  bucket = aws_s3_bucket.raw.id

  key = "glue-scripts/clickstream_gold_job.py"

  source = "${path.module}/../src/aws/glue/glue_job_gold.py"

  etag = filemd5("${path.module}/../src/aws/glue/glue_job_gold.py")
}

resource "aws_glue_crawler" "raw" {

  name = "clickstream-raw-crawler-${var.environment}"

  role = aws_iam_role.glue_role.name

  database_name = aws_glue_catalog_database.clickstream_db.name

  s3_target {
    path = "s3://${aws_s3_bucket.raw.id}/events/"
  }

  schema_change_policy {

    update_behavior = "UPDATE_IN_DATABASE"

    delete_behavior = "LOG"
  }

  configuration = jsonencode({
    Version = 1.0

    CrawlerOutput = {
      Partitions = {
        AddOrUpdateBehavior = "InheritFromTable"
      }
    }
  })

  tags = {
    Environment = var.environment
    Layer       = "raw"
  }

  depends_on = [
    aws_glue_catalog_database.clickstream_db,
    aws_s3_bucket.raw
  ]
}

resource "aws_glue_crawler" "silver" {

  name = "clickstream-silver-crawler-${var.environment}"

  role = aws_iam_role.glue_role.name

  database_name = aws_glue_catalog_database.clickstream_db.name

  s3_target {
    path = "s3://${aws_s3_bucket.silver.id}/clickstream-silver/"
  }

  schema_change_policy {

    update_behavior = "UPDATE_IN_DATABASE"

    delete_behavior = "LOG"
  }

  configuration = jsonencode({
    Version = 1.0

    CrawlerOutput = {
      Partitions = {
        AddOrUpdateBehavior = "InheritFromTable"
      }
    }
  })

  tags = {
    Environment = var.environment
    Layer       = "silver"
  }

  depends_on = [
    aws_glue_catalog_database.clickstream_db,
    aws_s3_bucket.silver
  ]
}

resource "aws_glue_crawler" "gold" {

  name = "clickstream-gold-crawler-${var.environment}"

  role = aws_iam_role.glue_role.name

  database_name = aws_glue_catalog_database.clickstream_db.name

  s3_target {
    path = "s3://${aws_s3_bucket.gold.id}/clickstream-gold/daily_events/"
  }

  s3_target {
    path = "s3://${aws_s3_bucket.gold.id}/clickstream-gold/funnel/"
  }

  s3_target {
    path = "s3://${aws_s3_bucket.gold.id}/clickstream-gold/product_performance/"
  }

  s3_target {
    path = "s3://${aws_s3_bucket.gold.id}/clickstream-gold/user_segments/"
  }

  schema_change_policy {

    update_behavior = "UPDATE_IN_DATABASE"

    delete_behavior = "LOG"
  }

  configuration = jsonencode({
    Version = 1.0

    CrawlerOutput = {
      Partitions = {
        AddOrUpdateBehavior = "InheritFromTable"
      }
    }
  })

  tags = {
    Environment = var.environment
    Layer       = "gold"
  }

  depends_on = [
    aws_glue_catalog_database.clickstream_db,
    aws_s3_bucket.gold
  ]
}

resource "aws_glue_job" "clickstream_etl" {

  name = "clickstream-glue-etl-${var.environment}"

  role_arn = aws_iam_role.glue_role.arn

  glue_version = var.glue_version

  worker_type = var.glue_worker_type

  number_of_workers = var.glue_number_of_workers

  execution_property {
    max_concurrent_runs = 1
  }

  command {

    name = "glueetl"

    python_version = "3"

    script_location = "s3://${aws_s3_object.glue_script.bucket}/${aws_s3_object.glue_script.key}"
  }

  default_arguments = {
    "--TempDir"      = "s3://${aws_s3_bucket.raw.id}/glue-temp/"
    "--job-language" = "python"

    "--job-bookmark-option" = "job-bookmark-enable"

    "--database" = aws_glue_catalog_database.clickstream_db.name
    "--table"    = "events"

    "--raw_path"    = "s3://${aws_s3_bucket.raw.id}/events/"
    "--silver_path" = "s3://${aws_s3_bucket.silver.id}/clickstream-silver/"

    "--enable-continuous-cloudwatch-log" = "true"
    "--enable-job-insights"              = "true"
  }

  depends_on = [
    aws_s3_object.glue_script,
    aws_glue_catalog_database.clickstream_db
  ]

  tags = {
    Environment = var.environment
  }
}

resource "aws_glue_job" "gold_etl" {

  name = "clickstream-glue-gold-${var.environment}"

  role_arn = aws_iam_role.glue_role.arn

  glue_version = var.glue_version

  worker_type = var.glue_worker_type

  number_of_workers = var.glue_number_of_workers

  execution_property {
    max_concurrent_runs = 1
  }

  command {

    name = "glueetl"

    python_version = "3"

    script_location = "s3://${aws_s3_object.gold_script.bucket}/${aws_s3_object.gold_script.key}"
  }

  default_arguments = {
    "--TempDir"      = "s3://${aws_s3_bucket.raw.id}/glue-temp/"
    "--job-language" = "python"

    "--job-bookmark-option" = "job-bookmark-enable"

    "--database" = aws_glue_catalog_database.clickstream_db.name
    "--table"    = "clickstream_silver"

    "--gold_path" = "s3://${aws_s3_bucket.gold.id}/clickstream-gold/"

    "--enable-continuous-cloudwatch-log" = "true"
    "--enable-job-insights"              = "true"
  }

  depends_on = [
    aws_s3_object.gold_script,
    aws_glue_catalog_database.clickstream_db
  ]

  tags = {
    Environment = var.environment
  }
}

output "glue_database_name" {
  value = aws_glue_catalog_database.clickstream_db.name
}

output "glue_job_name" {
  value = aws_glue_job.clickstream_etl.name
}

output "gold_job_name" {
  value = aws_glue_job.gold_etl.name
}

output "raw_crawler_name" {
  value = aws_glue_crawler.raw.name
}

output "silver_crawler_name" {
  value = aws_glue_crawler.silver.name
}

output "gold_crawler_name" {
  value = aws_glue_crawler.gold.name
}
