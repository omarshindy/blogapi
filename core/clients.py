import os
import boto3

# Get the credentials from environment variables
R2_ACCESS_KEY_ID = os.getenv('R2_ACCESS_KEY_ID')
R2_SECRET_ACCESS_KEY = os.getenv('R2_SECRET_ACCESS_KEY')
R2_ENDPOINT = os.getenv('R2_ENDPOINT')
R2_BUCKET_NAME = os.getenv('R2_BUCKET_NAME')


s3_client = boto3.client(
    's3',
    endpoint_url=R2_ENDPOINT,
    aws_access_key_id=R2_ACCESS_KEY_ID,
    aws_secret_access_key=R2_SECRET_ACCESS_KEY,
    config=boto3.session.Config(signature_version='s3v4')
)