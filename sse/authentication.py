from channels.db import database_sync_to_async
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import AnonymousUser

@database_sync_to_async
def get_user(token_key):
    try:
        return Token.objects.get(key=token_key).user
    except Token.DoesNotExist:
        return AnonymousUser()

class TokenAuthMiddleware:
    """
    Custom middleware for token based authentication.
    """

    def __init__(self, app):
        # Store the ASGI application we were passed
        self.app = app

    async def __call__(self, scope, receive, send):
        # TODO: Authentication
        headers = dict(scope['headers'])
        scope['user'] = AnonymousUser()
        if b'authorization' in headers:
            auth_string = headers[b'authorization'].decode()
            if auth_string.find(' ') != -1:
                token_name, token_key = auth_string.split(" ", 1)
                if token_name == 'Token':
                    scope['user'] = await get_user(token_key)
        return await self.app(scope, receive, send)