import json
import logging
import os

logger = logging.getLogger()
logger.setLevel(logging.INFO)

from src.producer.generate import (
    UserGenerator,
    ProductGenerator,
    SessionManager,
)
from src.producer.event_generator import ClickstreamGenerator
from src.aws.s3.s3_uploader import S3Uploader


def lambda_handler(event, context):
    num_users = int(event.get("num_users", os.environ.get("NUM_USERS", "50")))
    total_events = int(event.get("total_events", os.environ.get("TOTAL_EVENTS", "200")))
    buffer_size = int(event.get("buffer_size", os.environ.get("BUFFER_SIZE", "50")))
    bucket = event.get("bucket") or os.environ["S3_BUCKET"]
    prefix = event.get("prefix", os.environ.get("S3_PREFIX", "events"))

    logger.info(
        "Generating %s events with %s users, buffer=%s, bucket=%s, prefix=%s",
        total_events, num_users, buffer_size, bucket, prefix,
    )

    user_generator = UserGenerator(num_users=num_users)
    product_generator = ProductGenerator()
    session_manager = SessionManager()
    clickstream = ClickstreamGenerator(product_generator)
    uploader = S3Uploader(bucket_name=bucket, prefix=prefix)

    buffer = []

    for i in range(total_events):
        user = user_generator.random_user()
        session = session_manager.get_session(user)
        event = clickstream.generate_event(user=user, session=session)
        buffer.append(event)

        if len(buffer) >= buffer_size:
            uploader.upload_events(buffer)
            buffer.clear()

    if buffer:
        uploader.upload_events(buffer)

    logger.info("Finished generating %s events", total_events)

    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": f"Successfully generated {total_events} events",
            "bucket": bucket,
            "prefix": prefix,
        }),
    }
