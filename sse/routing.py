from django.urls import re_path
from channels.routing import URLRouter

from . import consumers

urlpatterns = URLRouter([
	re_path(r'', consumers.SseConsumer.as_asgi()),
])