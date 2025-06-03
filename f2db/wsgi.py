"""
WSGI config for f2db project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('F2_MODE', 'prod')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'f2db.settings')

application = get_wsgi_application()
