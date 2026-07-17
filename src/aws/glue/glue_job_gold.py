import sys

from pyspark.context import SparkContext
from pyspark.sql.functions import (
    col,
    count,
    countDistinct,
    sum as _sum,
    when,
    max as _max,
)

from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue.utils import getResolvedOptions


sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)

logger = glueContext.get_logger()


args = getResolvedOptions(
    sys.argv,
    [
        "JOB_NAME",
        "database",
        "table",
        "gold_path",
    ]
)

job.init(args["JOB_NAME"], args)

logger.info(f"Job initialized: {args['JOB_NAME']}")
logger.info(f"database={args['database']} table={args['table']} gold_path={args['gold_path']}")

SILVER = glueContext.create_dynamic_frame.from_catalog(
    database=args["database"],
    table_name=args["table"],
    transformation_ctx="silver_events",
)

df = SILVER.toDF().cache()

GOLD_PATH = args["gold_path"].rstrip("/")

EVENT_TYPES = [
    "login", "home", "search", "product_view", "add_to_cart",
    "remove_from_cart", "checkout", "payment", "payment_failed",
    "purchase", "logout",
]

FUNNEL_STAGES = [
    "login", "product_view", "add_to_cart", "checkout", "payment", "purchase",
]


def write_gold(subdir, data_frame, partition=False):
    path = f"{GOLD_PATH}/{subdir}"
    logger.info(f"Writing {subdir} to {path}...")
    writer = data_frame.write.mode("append").option("compression", "snappy")
    if partition:
        writer = writer.partitionBy("year", "month", "day")
    writer.parquet(path)
    logger.info(f"{subdir} write complete.")



daily_events = (
    df
    .groupBy("year", "month", "day")
    .agg(
        count("*").alias("total_events"),
        countDistinct("user_id").alias("unique_users"),
        countDistinct("session_id").alias("unique_sessions"),
        *[_sum(when(col("event_type") == et, 1).otherwise(0)).alias(f"{et}_count") for et in EVENT_TYPES],
    )
)

write_gold("daily_events", daily_events)

daily_count = daily_events.count()
logger.info(f"Daily events summary: {daily_count} day(s)")



funnel_per_session = (
    df
    .groupBy("session_id", "year", "month", "day")
    .agg(*[_max(when(col("event_type") == stage, 1).otherwise(0)).alias(f"has_{stage}") for stage in FUNNEL_STAGES])
)

funnel_agg = (
    funnel_per_session
    .groupBy("year", "month", "day")
    .agg(
        count("*").alias("total_sessions"),
        *[_sum(col(f"has_{stage}")).alias(f"{stage}_sessions") for stage in FUNNEL_STAGES],
    )
)

write_gold("funnel", funnel_agg)



product_perf = (
    df
    .filter(col("product_id").isNotNull())
    .groupBy("year", "month", "day", "product_id", "product_name", "product_category", "brand")
    .agg(
        _sum(when(col("event_type") == "product_view", 1).otherwise(0)).alias("views"),
        _sum(when(col("event_type") == "add_to_cart", 1).otherwise(0)).alias("add_to_cart"),
        _sum(when(col("event_type") == "purchase", 1).otherwise(0)).alias("purchases"),
        _sum(when(col("event_type") == "purchase", col("price")).otherwise(0)).alias("revenue"),
    )
)

write_gold("product_performance", product_perf, partition=True)

product_count = product_perf.count()
logger.info(f"Product performance: {product_count} product-day(s)")



user_segments = (
    df
    .groupBy("year", "month", "day", "country", "membership", "device")
    .agg(
        countDistinct("user_id").alias("user_count"),
        count("*").alias("event_count"),
    )
)

write_gold("user_segments", user_segments)



df.unpersist()
job.commit()
logger.info("Job committed successfully.")
