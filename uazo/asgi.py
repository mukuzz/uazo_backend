"""
ASGI config for uazo project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/howto/deployment/asgi/
"""

import os
from django.core.asgi import get_asgi_application
from django.urls import re_path
from channels.routing import ProtocolTypeRouter, URLRouter


# 
# DO NOT IMPORT ANYTHING ELSE BEFORE THIS
# 
# Fetch Django ASGI application early to ensure AppRegistry is populated
# before importing consumers and AuthMiddlewareStack that may import ORM
# models.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "uazo.settings")
django_asgi_app = get_asgi_application()

from sse import routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'uazo.settings')

application = ProtocolTypeRouter({
	"http": URLRouter([
		re_path(r'^sse/event/$', routing.urlpatterns),
		re_path(r'^.*$', django_asgi_app)
	])
})
