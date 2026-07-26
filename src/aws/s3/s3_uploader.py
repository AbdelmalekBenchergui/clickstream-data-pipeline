import json
from dataclasses import asdict
from datetime import datetime
from io import BytesIO

import boto3


class S3Uploader:

    def __init__(self, bucket_name, prefix="clickstream-raw"):

        self.bucket = bucket_name
        self.prefix = prefix

        self.s3 = boto3.client("s3")

    def upload_events(self, events):

        if len(events) == 0:
            return

        lines = []

        for event in events:

            lines.append(
                json.dumps(
                    asdict(event),
                    default=str
                )
            )

        data = "\n".join(lines)

        now = datetime.utcnow()

        key = (
            f"{self.prefix}/"
            f"year={now.year}/"
            f"month={now.month:02d}/"
            f"day={now.day:02d}/"
            f"events_{now.strftime('%H%M%S_%f')}.json"
        )

        self.s3.upload_fileobj(
            BytesIO(data.encode()),
            self.bucket,
            key
        )

        print(f"Uploaded {len(events)} events -> s3://{self.bucket}/{key}")