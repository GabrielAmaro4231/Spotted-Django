from hashlib import sha256
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from django.conf import settings


AVATAR_SIZE = 256
HTTP_TIMEOUT = 5
UI_AVATAR_PREFIX = 'profile_avatar_'
PROFILE_AVATAR_DIR = Path('public/media/profile')
REQUEST_HEADERS = {
    'User-Agent': 'SpottedAPI/1.0',
}


def get_email_hash(email):
    normalized_email = email.strip().lower()
    return sha256(normalized_email.encode('utf-8')).hexdigest()


def get_gravatar_url(email_hash):
    query_params = urlencode({
        's': AVATAR_SIZE,
        'd': '404',
    })
    return f'https://gravatar.com/avatar/{email_hash}?{query_params}'


def gravatar_exists(gravatar_url):
    if request_succeeds(gravatar_url, method='HEAD'):
        return True

    return request_succeeds(gravatar_url, method='GET')


def request_succeeds(url, method):
    request = Request(url, headers=REQUEST_HEADERS, method=method)

    try:
        with urlopen(request, timeout=HTTP_TIMEOUT) as response:
            return response.status == 200
    except HTTPError as error:
        if error.code == 404:
            return False
    except URLError:
        return False

    return False


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


def download_ui_avatar(email_hash):
    avatar_url = get_ui_avatar_url(email_hash)
    request = Request(avatar_url, headers=REQUEST_HEADERS)

    try:
        with urlopen(request, timeout=HTTP_TIMEOUT) as response:
            if response.status != 200:
                return ''

            content_type = response.headers.get('Content-Type', '')

            if not content_type.startswith('image/'):
                return ''

            filename = f'{UI_AVATAR_PREFIX}{email_hash}.png'
            avatar_directory = Path(settings.BASE_DIR) / PROFILE_AVATAR_DIR
            avatar_directory.mkdir(parents=True, exist_ok=True)
            relative_path = PROFILE_AVATAR_DIR / filename
            avatar_path = Path(settings.BASE_DIR) / relative_path
            avatar_path.write_bytes(response.read())

            return str(relative_path)
    except (HTTPError, URLError, OSError):
        return ''


def get_profile_image_for_email(email):
    email_hash = get_email_hash(email)
    gravatar_url = get_gravatar_url(email_hash)

    if gravatar_exists(gravatar_url):
        return gravatar_url

    return download_ui_avatar(email_hash)
