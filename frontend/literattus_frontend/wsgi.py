"""
WSGI config for literattus_frontend project.
"""

import os

# Configure logging BEFORE Django initialization
from literattus_frontend.logging_config import logger

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'literattus_frontend.settings')

application = get_wsgi_application()

logger.info("WSGI application initialized")

