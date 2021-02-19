"""
ASGI config for uazo_api_server project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/howto/deployment/asgi/
"""

import os
from django.core.asgi import get_asgi_application
from django.urls import re_path
from channels.routing import ProtocolTypeRouter, URLRouter

from sse import routing

# Fetch Django ASGI application early to ensure AppRegistry is populated
# before importing consumers and AuthMiddlewareStack that may import ORM
# models.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "uazo_api_server.settings")
django_asgi_app = get_asgi_application()

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'uazo_api_server.settings')

application = ProtocolTypeRouter({
	"http": URLRouter([
		re_path(r'^sse/event/$', routing.urlpatterns),
		re_path(r'^.*$', django_asgi_app)
	])
})
