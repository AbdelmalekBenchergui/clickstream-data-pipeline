import sys

from pyspark.context import SparkContext
from pyspark.sql.functions import (
    col,
    to_timestamp,
    year,
    month,
    dayofmonth,
)

from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue.utils import getResolvedOptions



sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)

logger = glueContext.get_logger()


TIMESTAMP_FORMAT = None

FILES_PER_DAY_PARTITION = 4



args = getResolvedOptions(
    sys.argv,
    [
        "JOB_NAME",
        "database",
        "table",
        "silver_path",
        "raw_path",
    ]
)

job.init(args["JOB_NAME"], args)

logger.info(f"Job initialized: {args['JOB_NAME']}")
logger.info(f"database={args['database']} table={args['table']} raw_path={args['raw_path']} silver_path={args['silver_path']}")





raw = glueContext.create_dynamic_frame.from_catalog(
    database=args["database"],
    table_name=args["table"],
    transformation_ctx="raw_events",
)

df = raw.toDF()




silver = (
    df
    .select(
        col("event_id"),
        col("event_type"),
        col("timestamp"),
        col("session_id"),
        col("user_id"),

        col("payload.user.country").alias("country"),
        col("payload.user.city").alias("city"),
        col("payload.user.membership").alias("membership"),
        col("payload.user.favorite_category").alias("favorite_category"),

        col("payload.session.browser").alias("browser"),
        col("payload.session.device").alias("device"),
        col("payload.session.current_page").alias("current_page"),

        col("payload.product.product_id").alias("product_id"),
        col("payload.product.name").alias("product_name"),
        col("payload.product.category").alias("product_category"),
        col("payload.product.brand").alias("brand"),
        col("payload.product.price").alias("price"),

        col("payload.search_query").alias("search_query"),

        col("payload.cart.items").alias("cart_items"),
        col("payload.cart.total").alias("cart_total"),

        col("payload.checkout.items").alias("checkout_items"),
        col("payload.checkout.subtotal").alias("checkout_subtotal"),
        col("payload.checkout.shipping").alias("shipping"),
        col("payload.checkout.tax").alias("tax"),

        col("payload.payment.method").alias("payment_method"),

        col("payload.order.order_id").alias("order_id"),
        col("payload.order.items").alias("order_items"),
        col("payload.order.subtotal").alias("order_subtotal"),
        col("payload.order.tax").alias("order_tax"),
        col("payload.order.shipping").alias("order_shipping"),
        col("payload.order.total").alias("order_total"),
    )
)


if TIMESTAMP_FORMAT:
    silver = silver.withColumn(
        "event_timestamp",
        to_timestamp(col("timestamp"), TIMESTAMP_FORMAT)
    )
else:
    silver = silver.withColumn(
        "event_timestamp",
        to_timestamp(col("timestamp"))
    )

silver = silver.drop("timestamp")


silver = (
    silver
    .withColumn("year", year("event_timestamp"))
    .withColumn("month", month("event_timestamp"))
    .withColumn("day", dayofmonth("event_timestamp"))
)



total_rows = silver.count()

null_ts = silver.filter(col("event_timestamp").isNull()).count()
null_event_id = silver.filter(col("event_id").isNull()).count()
null_user_id = silver.filter(col("user_id").isNull()).count()

logger.info(
    f"Pre-filter row count: {total_rows} | "
    f"null event_timestamp: {null_ts} | "
    f"null event_id: {null_event_id} | "
    f"null user_id: {null_user_id}"
)

silver = silver.dropDuplicates(["event_id"])

silver = silver.filter(col("event_timestamp").isNotNull())
silver = silver.filter(col("event_id").isNotNull())
silver = silver.filter(col("user_id").isNotNull())

post_filter_rows = silver.count()
logger.info(
    f"Post-filter row count: {post_filter_rows} "
    f"(dropped {total_rows - post_filter_rows} rows)"
)



silver = silver.repartition(FILES_PER_DAY_PARTITION, "year", "month", "day")

logger.info(f"Writing Silver Parquet to {args['silver_path']}...")

(
    silver
    .write
    .mode("append")
    .option("compression", "snappy")
    .partitionBy(
        "year",
        "month",
        "day",
    )
    .parquet(
        args["silver_path"]
    )
)

logger.info("Silver write complete.")



job.commit()

logger.info("Job committed successfully.")
