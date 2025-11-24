from urllib.parse import parse_qs
from channels.db import database_sync_to_async
from channels.middleware import BaseMiddleware
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError

User = get_user_model()


@database_sync_to_async
def get_user_from_token(token_key):
    try:
        # Validate the token
        access_token = AccessToken(token_key)
        user_id = access_token['user_id']
        
        # Get the user
        user = User.objects.get(id=user_id)
        return user
    except (InvalidToken, TokenError, User.DoesNotExist) as e:
        print(f"[JWT Middleware] Token validation failed: {e}")
        return AnonymousUser()


class JWTAuthMiddleware(BaseMiddleware):
    """
    Custom middleware that takes a JWT token from the query string
    and authenticates the user.
    """

    async def __call__(self, scope, receive, send):
        # Get the token from query string
        query_string = scope.get('query_string', b'').decode()
        query_params = parse_qs(query_string)
        token = query_params.get('token', [None])[0]

        if token:
            print(f"[JWT Middleware] Token found in query string")
            scope['user'] = await get_user_from_token(token)
            print(f"[JWT Middleware] Authenticated user: {scope['user']}")
        else:
            print(f"[JWT Middleware] No token found in query string")
            scope['user'] = AnonymousUser()

        return await super().__call__(scope, receive, send)
