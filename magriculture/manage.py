#!/usr/bin/env python
from django.core.management import execute_manager
import imp
import logging
import sys
import traceback
try:
    imp.find_module('settings')  # Assumed to be in the same directory.
except ImportError:
    sys.stderr.write("Error: Can't find the file 'settings.py' in the "\
            "directory containing %r. It appears you've customized things.\n"\
            "You'll have to run django-admin.py, passing it your settings "\
            "module.\n" % __file__)
    sys.exit(1)

import settings

if __name__ == '__main__':
    try:
        execute_manager(settings)
    except Exception, e:
        # Log errors to Sentry.
        exc_info = sys.exc_info()
        logging.error(e, exc_info=exc_info)
        traceback.print_exc()
