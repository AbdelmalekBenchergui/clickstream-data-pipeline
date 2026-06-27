import time

from src.producer.generate import (
    UserGenerator,
    ProductGenerator,
    SessionManager,
)

from src.producer.event_generator import ClickstreamGenerator
from src.aws.s3.s3_uploader import S3Uploader
import os


from dotenv import load_dotenv

load_dotenv()

BUCKET_NAME = os.getenv("S3_BUCKET")
PREFIX = os.getenv("S3_PREFIX")

NUM_USERS = int(os.getenv("NUM_USERS", 50))
EVENTS_PER_SECOND = int(os.getenv("EVENTS_PER_SECOND", 20))
BUFFER_SIZE = int(os.getenv("BUFFER_SIZE", 100))
TOTAL_EVENTS = int(os.getenv("TOTAL_EVENTS", 1000))


def main():

    print("Creating users...")
    user_generator = UserGenerator(num_users=100)

    print("Creating products...")
    product_generator = ProductGenerator()

    print("Creating sessions...")
    session_manager = SessionManager()

    print("Creating clickstream generator...")
    clickstream = ClickstreamGenerator(product_generator)

    print("Connecting to S3...")
    uploader = S3Uploader(
        bucket_name=BUCKET_NAME,
        prefix=PREFIX
    )

    buffer = []

    print("\nGenerating events...\n")

    for _ in range(TOTAL_EVENTS):

        user = user_generator.random_user()

        session = session_manager.get_session(user)

        event = clickstream.generate_event(
            user=user,
            session=session
        )

        buffer.append(event)

        if len(buffer) >= BUFFER_SIZE:

            uploader.upload_events(buffer)

            buffer.clear()

        time.sleep(0.05)

    if buffer:
        uploader.upload_events(buffer)

    print("\nFinished.")


if __name__ == "__main__":
    main()