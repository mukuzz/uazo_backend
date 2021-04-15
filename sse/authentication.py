from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser

class TokenAuthMiddleware:
    """
    Custom middleware for token based authentication.
    """
    model = None

    def __init__(self, app):
        # Store the ASGI application we were passed
        self.app = app

    def get_model(self):
        if self.model is not None:
            return self.model
        from rest_framework.authtoken.models import Token
        return Token
    
    @database_sync_to_async
    def get_user(self, token_key):
        try:
            model = self.get_model()
            return model.objects.get(key=token_key).user
        except model.DoesNotExist:
            return AnonymousUser()

    async def __call__(self, scope, receive, send):
        # TODO: Authentication
        headers = dict(scope['headers'])
        scope['user'] = AnonymousUser()
        if b'authorization' in headers:
            auth_string = headers[b'authorization'].decode()
            if auth_string.find(' ') != -1:
                token_name, token_key = auth_string.split(" ", 1)
                if token_name == 'Token':
                    scope['user'] = await self.get_user(token_key)
        return await self.app(scope, receive, send)