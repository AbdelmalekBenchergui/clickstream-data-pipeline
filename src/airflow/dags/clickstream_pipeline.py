from datetime import datetime

from airflow import DAG
from airflow.models import Variable
from airflow.providers.amazon.aws.operators.glue import GlueJobOperator
from airflow.providers.amazon.aws.operators.glue_crawler import GlueCrawlerOperator

ENVIRONMENT = Variable.get("ENVIRONMENT", default_var="dev")

DATABASE = f"clickstream_db-{ENVIRONMENT}"

CRAWLER_RAW    = f"clickstream-raw-crawler-{ENVIRONMENT}"
CRAWLER_SILVER = f"clickstream-silver-crawler-{ENVIRONMENT}"
CRAWLER_GOLD   = f"clickstream-gold-crawler-{ENVIRONMENT}"

JOB_SILVER = f"clickstream-glue-etl-{ENVIRONMENT}"
JOB_GOLD   = f"clickstream-glue-gold-{ENVIRONMENT}"

with DAG(
    dag_id="clickstream_pipeline",
    description="Clickstream medallion pipeline: raw → silver → gold",
    start_date=datetime(2024, 1, 1),
    schedule="@hourly",
    catchup=False,
    tags=["clickstream", "medallion"],
) as dag:

    crawl_raw = GlueCrawlerOperator(
        task_id="crawl_raw_data",
        config={"Name": CRAWLER_RAW},
        wait_for_completion=True,
        poll_interval=10,
    )

    run_silver_etl = GlueJobOperator(
        task_id="run_silver_etl",
        job_name=JOB_SILVER,
        script_args={
            "--database": DATABASE,
            "--table": "events",
        },
        wait_for_completion=True,
        verbose=True,
    )

    crawl_silver = GlueCrawlerOperator(
        task_id="crawl_silver_data",
        config={"Name": CRAWLER_SILVER},
        wait_for_completion=True,
        poll_interval=10,
    )

    run_gold_etl = GlueJobOperator(
        task_id="run_gold_etl",
        job_name=JOB_GOLD,
        script_args={
            "--database": DATABASE,
            "--table": "clickstream_silver",
        },
        wait_for_completion=True,
        verbose=True,
    )

    crawl_gold = GlueCrawlerOperator(
        task_id="crawl_gold_data",
        config={"Name": CRAWLER_GOLD},
        wait_for_completion=True,
        poll_interval=10,
    )

    crawl_raw >> run_silver_etl >> crawl_silver >> run_gold_etl >> crawl_gold
