import os
from settings import *

MAGRICULTURE_TEST_DB = os.environ.get('MAGRICULTURE_TEST_DB', 'memory')

if MAGRICULTURE_TEST_DB == "sqlite":
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': 'magriculture.db',
        }
    }

elif MAGRICULTURE_TEST_DB == "postgres":
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': 'magriculture',
            'USER': 'magriculture',
            'PASSWORD': 'magriculture',
            'HOST': 'localhost',
        }
    }

elif MAGRICULTURE_TEST_DB == "memory":
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': ':memory:',
        }
    }

else:
    raise ValueError("Invalid value %r for MAGRICULTURE_TEST_DB"
                     % MAGRICULTURE_TEST_DB)

del MAGRICULTURE_TEST_DB

if os.environ.get('MAGRICULTURE_FAST_TESTS'):
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': ':memory:',
        }
    }

NOSE_ARGS = ['-eworkers', '-m^test']
