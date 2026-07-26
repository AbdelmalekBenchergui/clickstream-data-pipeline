import time
import os
from dotenv import load_dotenv

load_dotenv()

from src.producer.generate import (
    UserGenerator,
    ProductGenerator,
    SessionManager,
)
from src.producer.event_generator import ClickstreamGenerator
from src.aws.s3.s3_uploader import S3Uploader

S3_BUCKET = os.getenv("S3_BUCKET")
S3_PREFIX = os.getenv("S3_PREFIX")
NUM_USERS = int(os.getenv("NUM_USERS", 50))
EVENTS_PER_SEC = int(os.getenv("EVENTS_PER_SEC", 15))
BUFFER_SIZE = int(os.getenv("BUFFER_SIZE", 150))


def main():

    print("Creating users...")
    user_generator = UserGenerator(num_users=NUM_USERS)

    print("Creating products...")
    product_generator = ProductGenerator()

    print("Creating sessions...")
    session_manager = SessionManager()

    print("Creating clickstream generator...")
    clickstream = ClickstreamGenerator(product_generator)

    print("Connecting to S3...")
    uploader = S3Uploader(bucket_name=S3_BUCKET, prefix=S3_PREFIX)

    buffer = []
    interval = 1.0 / EVENTS_PER_SEC

    print(f"\nGenerating events at ~{EVENTS_PER_SEC}/sec (buffer={BUFFER_SIZE})...\n")

    while True:

        user = user_generator.random_user()
        session = session_manager.get_session(user)
        event = clickstream.generate_event(user=user, session=session)
        buffer.append(event)

        if len(buffer) >= BUFFER_SIZE:
            uploader.upload_events(buffer)
            buffer.clear()

        time.sleep(interval)


if __name__ == "__main__":
    main()