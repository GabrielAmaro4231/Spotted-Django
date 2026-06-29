import logging
from io import BytesIO
from urllib.parse import quote

import boto3
from botocore.exceptions import BotoCoreError, ClientError
from django.conf import settings


logger = logging.getLogger(__name__)


def get_s3_client():
    client_options = {}

    if settings.AWS_S3_REGION_NAME:
        client_options['region_name'] = settings.AWS_S3_REGION_NAME

    if settings.AWS_S3_ENDPOINT_URL:
        client_options['endpoint_url'] = settings.AWS_S3_ENDPOINT_URL

    return boto3.client('s3', **client_options)


def get_s3_object_url(key):
    quoted_key = quote(key)

    if settings.AWS_S3_CUSTOM_DOMAIN:
        custom_domain = settings.AWS_S3_CUSTOM_DOMAIN.rstrip('/')

        if custom_domain.startswith(('http://', 'https://')):
            return f'{custom_domain}/{quoted_key}'

        return f'https://{custom_domain}/{quoted_key}'

    bucket = settings.AWS_STORAGE_BUCKET_NAME

    if settings.AWS_S3_ENDPOINT_URL:
        return f'{settings.AWS_S3_ENDPOINT_URL.rstrip("/")}/{bucket}/{quoted_key}'

    if settings.AWS_S3_REGION_NAME and settings.AWS_S3_REGION_NAME != 'us-east-1':
        return f'https://{bucket}.s3.{settings.AWS_S3_REGION_NAME}.amazonaws.com/{quoted_key}'

    return f'https://{bucket}.s3.amazonaws.com/{quoted_key}'


def upload_profile_avatar(content, filename, content_type):
    if not settings.AWS_STORAGE_BUCKET_NAME:
        logger.warning('Profile avatar upload skipped: AWS_STORAGE_BUCKET_NAME is not configured')
        return ''

    prefix = settings.AWS_S3_PROFILE_AVATAR_PREFIX.strip('/')
    key = f'{prefix}/{filename}' if prefix else filename
    extra_args = {
        'ContentType': content_type,
        'CacheControl': 'public, max-age=31536000',
    }

    if settings.AWS_S3_OBJECT_ACL:
        extra_args['ACL'] = settings.AWS_S3_OBJECT_ACL

    try:
        get_s3_client().upload_fileobj(
            BytesIO(content),
            settings.AWS_STORAGE_BUCKET_NAME,
            key,
            ExtraArgs=extra_args,
        )
    except (BotoCoreError, ClientError, OSError):
        logger.exception('Profile avatar upload to S3 failed')
        return ''

    return get_s3_object_url(key)
