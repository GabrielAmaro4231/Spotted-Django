from dataclasses import dataclass
from hashlib import sha256
from mimetypes import guess_extension
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from .storage_service import upload_profile_avatar


AVATAR_SIZE = 256
HTTP_TIMEOUT = 5
UI_AVATAR_PREFIX = 'profile_avatar_'
REQUEST_HEADERS = {
    'User-Agent': 'SpottedAPI/1.0',
}


@dataclass
class DownloadedImage:
    content: bytes
    content_type: str


def get_email_hash(email):
    normalized_email = email.strip().lower()
    return sha256(normalized_email.encode('utf-8')).hexdigest()


def get_gravatar_url(email_hash):
    query_params = urlencode({
        's': AVATAR_SIZE,
        'd': '404',
    })
    return f'https://gravatar.com/avatar/{email_hash}?{query_params}'


def download_image(url):
    request = Request(url, headers=REQUEST_HEADERS)

    try:
        with urlopen(request, timeout=HTTP_TIMEOUT) as response:
            if response.status != 200:
                return None

            content_type = response.headers.get('Content-Type', '').split(';')[0].strip()

            if not content_type.startswith('image/'):
                return None

            return DownloadedImage(
                content=response.read(),
                content_type=content_type,
            )
    except HTTPError as error:
        if error.code == 404:
            return None
    except URLError:
        return None

    return None


def get_ui_avatar_url(email_hash):
    query_params = urlencode({
        'name': email_hash,
        'size': AVATAR_SIZE,
        'format': 'png',
        'background': 'random',
        'length': 2,
        'bold': 'true',
    })
    return f'https://ui-avatars.com/api/?{query_params}'


def get_file_extension(content_type):
    extension = guess_extension(content_type) or '.png'

    if extension == '.jpe':
        return '.jpg'

    return extension


def upload_avatar(image, email_hash, source):
    extension = get_file_extension(image.content_type)
    filename = f'{UI_AVATAR_PREFIX}{source}_{email_hash}{extension}'
    return upload_profile_avatar(image.content, filename, image.content_type)


def get_profile_image_for_email(email):
    email_hash = get_email_hash(email)
    gravatar_image = download_image(get_gravatar_url(email_hash))

    if gravatar_image:
        return upload_avatar(gravatar_image, email_hash, 'gravatar')

    ui_avatar_image = download_image(get_ui_avatar_url(email_hash))

    if ui_avatar_image:
        return upload_avatar(ui_avatar_image, email_hash, 'generated')

    return ''
