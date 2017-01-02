from .base import *


MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
STATICFILES_DIRS = [
    MEDIA_ROOT,
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'tmb',
        'USER': 'root',
        'PASSWORD': 'akdldptmzbdpf',
        'HOST': '127.0.0.1',
        'PORT': '3306',
    }
}

# use sqlite3 for testing in local as it's much faster.
if IN_TESTING:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(BASE_DIR, 'testdb.sqlite3'),
        }
    }
