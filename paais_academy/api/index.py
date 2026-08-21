import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PROJECT_DIR = os.path.join(BASE_DIR, "paais_academy")

if PROJECT_DIR not in sys.path:
    sys.path.insert(0, PROJECT_DIR)

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "paais_academy.settings"
)

from django.core.wsgi import get_wsgi_application

app = get_wsgi_application()