import os
import sys

# Get the root directory of the deployed project
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Path to the Django project directory
PROJECT_DIR = os.path.join(BASE_DIR, "paais_academy")

# Make Django project importable
if PROJECT_DIR not in sys.path:
    sys.path.insert(0, PROJECT_DIR)

# Tell Django which settings module to use
os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "paais_academy.settings"
)

# Load Django
from django.core.wsgi import get_wsgi_application

# Vercel looks for this callable
app = get_wsgi_application()