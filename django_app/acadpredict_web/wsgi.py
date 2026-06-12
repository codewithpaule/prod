"""WSGI config for acadpredict_web."""
import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "acadpredict_web.settings")

application = get_wsgi_application()
