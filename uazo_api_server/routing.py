from django.urls import re_path
from channels.routing import URLRouter
from django.core.asgi import get_asgi_application

from sse import routing

urlpatterns = URLRouter([
	re_path(r'sse/event/', routing.urlpatterns),
	re_path(r'^.*$', get_asgi_application())
])