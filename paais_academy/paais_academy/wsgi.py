import os
import django
from pathlib import Path
from django.conf import settings
from django.core.wsgi import get_wsgi_application
from django.core.management import call_command
from whitenoise import WhiteNoise

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'paais_academy.settings')

# Setup Django
django.setup()

# Get WSGI application
application = get_wsgi_application()

# Add WhiteNoise middleware for static files
application = WhiteNoise(
    application,
    root=os.path.join(Path(__file__).resolve().parent, 'staticfiles'),
    mimetypes={
        '.webmanifest': 'application/manifest+json',
    }
)

# ADD THIS LINE FOR VERCEL:
app = application

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
