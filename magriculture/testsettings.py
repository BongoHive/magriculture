import os
from settings import *


if os.environ.get('MAGRICULTURE_FAST_TESTS'):
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': ':memory:',
        }
    }

NOSE_ARGS = ['-eworkers', '-m^test']
