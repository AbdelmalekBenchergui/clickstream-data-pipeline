#!/bin/bash
set -euo pipefail

BUNDLE_S3="s3://${S3_BUCKET}/clickstream-raw/producer-bundle.zip"
REPO_DIR=/home/ec2-user/clickstream-lakehouse

yum update -y
yum install -y python3 python3-pip unzip

pip3 install boto3 Faker python-dotenv

aws s3 cp "$BUNDLE_S3" /tmp/producer-bundle.zip
mkdir -p $REPO_DIR
unzip -o /tmp/producer-bundle.zip -d $REPO_DIR
rm -f /tmp/producer-bundle.zip

chown -R ec2-user:ec2-user $REPO_DIR

cat > /etc/systemd/system/clickstream-producer.service << 'SERVICE'
[Unit]
Description=Clickstream Producer Service
After=network.target

[Service]
Type=simple
User=ec2-user
WorkingDirectory=${REPO_DIR}/src
Environment=PYTHONPATH=${REPO_DIR}/src
Environment=S3_BUCKET=${S3_BUCKET}
Environment=S3_PREFIX=${S3_PREFIX}
Environment=NUM_USERS=${NUM_USERS}
Environment=EVENTS_PER_SEC=${EVENTS_PER_SEC}
Environment=BUFFER_SIZE=150
ExecStart=/usr/bin/python3 ${REPO_DIR}/src/producer/producer.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
SERVICE

systemctl daemon-reload
systemctl enable clickstream-producer
systemctl start clickstream-producer
