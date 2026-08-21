import os
import django
from pathlib import Path
from django.conf import settings
from django.core.wsgi import get_wsgi_application
from django.core.management import call_command
from whitenoise import WhiteNoise

# Set Django settings module
# Add the outer Django project directory to Python's import path.
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "paais_academy.settings"
)

# Add WhiteNoise middleware for static files
application = WhiteNoise(
    application,
    root=os.path.join(Path(__file__).resolve().parent, 'staticfiles'),
    mimetypes={
        '.webmanifest': 'application/manifest+json',
    }
)


# Run migrations on startup (optional - for Render.com or similar)
if os.getenv('RUN_MIGRATIONS') == 'true':
    try:
        call_command('migrate', '--noinput')
    except Exception as e:
        print(f"Migration error: {e}")

# Load sample data if needed
if os.getenv('LOAD_SAMPLE_DATA') == 'true':
    try:
        call_command('load_sample_data')
    except Exception as e:
        print(f"Sample data load error: {e}")

# Health checks are handled by the Django URL at /health/ and /api/v1/health/.
# Keep the WSGI callable unwrapped so Django middleware and URL routing work normally.
