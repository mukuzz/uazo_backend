"""
ASGI config for uazo_api_server project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/howto/deployment/asgi/
"""

import os

from channels.routing import ProtocolTypeRouter
from . import routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'uazo_api_server.settings')

application = ProtocolTypeRouter({
	"http": routing.urlpatterns
})
