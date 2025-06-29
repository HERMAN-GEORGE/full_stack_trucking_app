import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'full_stack_trucking_app.settings')

application = get_asgi_application()
