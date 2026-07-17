# Clickstream Glue ETL

This folder contains the Glue ETL jobs for the clickstream medallion data lake.

## Jobs

- `glue_job_silver.py`: reads raw JSONL events from Glue Catalog (`events` table), flattens the nested payload, deduplicates, filters nulls, and writes Snappy-compressed Parquet to the Silver layer partitioned by `year/month/day`.

- `glue_job_gold.py`: reads Silver Parquet from Glue Catalog (`clickstream_silver` table), computes 4 aggregations (daily events, conversion funnel, product performance, user segments), and writes to the Gold layer.

## Terraform references

Both scripts are uploaded and configured via `terraform/glue.tf`:
- `aws_glue_job.clickstream_etl` → `glue_job_silver.py`
- `aws_glue_job.gold_etl` → `glue_job_gold.py`

## Output layout

- Silver: Snappy Parquet, partitioned by `year/month/day`, S3 path `clickstream-silver/`
- Gold: Snappy Parquet, 4 subdirectories under `clickstream-gold/`:
  - `daily_events/` — per-day event counts and unique users/sessions
  - `funnel/` — session-level conversion funnel stages
  - `product_performance/` — per-product views, add-to-cart, purchases
  - `user_segments/` — per-segment user and event counts (by country, membership, device)

## Pipeline order

```bash
aws glue start-crawler --name clickstream-raw-crawler-dev
aws glue start-job-run --job-name clickstream-glue-etl-dev
aws glue start-crawler --name clickstream-silver-crawler-dev
aws glue start-job-run --job-name clickstream-glue-gold-dev
aws glue start-crawler --name clickstream-gold-crawler-dev
```

## Notes

- The raw layer stays as JSONL.
- Glue and Athena work best with Parquet in the curated layers.
- You can run the scripts in AWS Glue or locally with PySpark for testing.
