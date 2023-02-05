from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework import status


class CustomAuthFailed(AuthenticationFailed):
    def __init__(self, detail=None, code=None, status=status.HTTP_401_UNAUTHORIZED):
        super().__init__(detail=detail, code=code)
        self.status = status


class CustomJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        try:
            user, jwt_value = super().authenticate(request)
            return user, jwt_value
        except Exception as e:
            raise CustomAuthFailed({'error': 'Token is invalid or expired'}, status=status.HTTP_401_UNAUTHORIZED)
