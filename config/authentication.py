from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from users.models import User
import jwt
from django.conf import settings


class TrustMeBroAuthentication(BaseAuthentication):
    def authenticate(self, request):
        username = request.headers.get("Trust-me")
        if not username:
            return None
        try:
            user = User.objects.get(username=username)
            return (user, None)  # 규칙임
        except User.DoesNotExist:
            raise AuthenticationFailed(f"no user {username}")


class JWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        token = request.headers.get("Jwt")
        if not token:
            return None
        decoded = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=["HS256"],
        )
        pk = decoded["pk"]
        if not pk:
            raise AuthenticationFailed("Invalid Token")
        try:
            user = User.objects.get(pk=pk)
            return (user, None)
        except User.DoesNotExist:
            raise AuthenticationFailed("User not Found")
