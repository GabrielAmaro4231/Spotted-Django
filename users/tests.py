from hashlib import sha256
from unittest import mock

from django.test import SimpleTestCase, override_settings

from .avatar_service import (
    DownloadedImage,
    get_gravatar_url,
    get_profile_image_for_email,
    get_ui_avatar_url,
)
from .storage_service import get_s3_object_url, upload_profile_avatar


class AvatarServiceTests(SimpleTestCase):
    def test_gravatar_image_is_uploaded_to_s3(self):
        email_hash = sha256('user@example.com'.encode('utf-8')).hexdigest()
        image = DownloadedImage(content=b'gravatar-image', content_type='image/jpeg')

        with mock.patch('users.avatar_service.download_image') as download_image:
            with mock.patch('users.avatar_service.upload_profile_avatar') as upload_profile_avatar_mock:
                download_image.return_value = image
                upload_profile_avatar_mock.return_value = 'https://cdn.example.com/profile/avatar.jpg'

                profile_image_url = get_profile_image_for_email('User@Example.com')

        self.assertEqual(profile_image_url, 'https://cdn.example.com/profile/avatar.jpg')
        download_image.assert_called_once_with(get_gravatar_url(email_hash))
        upload_profile_avatar_mock.assert_called_once_with(
            b'gravatar-image',
            f'profile_avatar_gravatar_{email_hash}.jpg',
            'image/jpeg',
        )

    def test_generated_avatar_is_uploaded_to_s3_when_gravatar_is_missing(self):
        email_hash = sha256('user@example.com'.encode('utf-8')).hexdigest()
        image = DownloadedImage(content=b'generated-image', content_type='image/png')

        with mock.patch('users.avatar_service.download_image') as download_image:
            with mock.patch('users.avatar_service.upload_profile_avatar') as upload_profile_avatar_mock:
                download_image.side_effect = [None, image]
                upload_profile_avatar_mock.return_value = 'https://cdn.example.com/profile/avatar.png'

                profile_image_url = get_profile_image_for_email('User@Example.com')

        self.assertEqual(profile_image_url, 'https://cdn.example.com/profile/avatar.png')
        self.assertEqual(
            download_image.call_args_list,
            [
                mock.call(get_gravatar_url(email_hash)),
                mock.call(get_ui_avatar_url(email_hash)),
            ],
        )
        upload_profile_avatar_mock.assert_called_once_with(
            b'generated-image',
            f'profile_avatar_generated_{email_hash}.png',
            'image/png',
        )


class S3StorageServiceTests(SimpleTestCase):
    @override_settings(
        AWS_STORAGE_BUCKET_NAME='spotted-assets',
        AWS_S3_REGION_NAME='sa-east-1',
        AWS_S3_CUSTOM_DOMAIN='https://cdn.example.com',
        AWS_S3_ENDPOINT_URL='',
        AWS_S3_PROFILE_AVATAR_PREFIX='profile/',
        AWS_S3_OBJECT_ACL='',
    )
    def test_upload_profile_avatar_uses_boto3_and_returns_s3_url(self):
        s3_client = mock.Mock()

        with mock.patch('users.storage_service.boto3.client', return_value=s3_client) as boto3_client:
            profile_image_url = upload_profile_avatar(
                b'avatar-content',
                'avatar.png',
                'image/png',
            )

        self.assertEqual(profile_image_url, 'https://cdn.example.com/profile/avatar.png')
        boto3_client.assert_called_once_with('s3', region_name='sa-east-1')
        upload_args, upload_kwargs = s3_client.upload_fileobj.call_args
        self.assertEqual(upload_args[0].getvalue(), b'avatar-content')
        self.assertEqual(upload_args[1], 'spotted-assets')
        self.assertEqual(upload_args[2], 'profile/avatar.png')
        self.assertEqual(upload_kwargs['ExtraArgs']['ContentType'], 'image/png')

    @override_settings(
        AWS_STORAGE_BUCKET_NAME='spotted-assets',
        AWS_S3_REGION_NAME='sa-east-1',
        AWS_S3_CUSTOM_DOMAIN='',
        AWS_S3_ENDPOINT_URL='',
    )
    def test_s3_object_url_uses_bucket_region_when_custom_domain_is_missing(self):
        self.assertEqual(
            get_s3_object_url('profile/avatar.png'),
            'https://spotted-assets.s3.sa-east-1.amazonaws.com/profile/avatar.png',
        )

    @override_settings(AWS_STORAGE_BUCKET_NAME='')
    def test_upload_profile_avatar_returns_empty_string_without_bucket(self):
        with mock.patch('users.storage_service.boto3.client') as boto3_client:
            with mock.patch('users.storage_service.logger.warning') as warning:
                profile_image_url = upload_profile_avatar(
                    b'avatar-content',
                    'avatar.png',
                    'image/png',
                )

        self.assertEqual(profile_image_url, '')
        boto3_client.assert_not_called()
        warning.assert_called_once_with(
            'Profile avatar upload skipped: AWS_STORAGE_BUCKET_NAME is not configured'
        )
