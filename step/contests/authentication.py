import jwt
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import authentication
from rest_framework.exceptions import AuthenticationFailed
from jwt import ExpiredSignatureError, InvalidTokenError

User = get_user_model()


# кастомная аутентификация через JWT токены, полученные в Центре пользователей Cloveri
class JWTAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        jwt_token = request.META.get('HTTP_AUTHORIZATION')
        if jwt_token is None:
            return None
        public_key = settings.ACCESS_TOKEN_PUBLIC_KEY.replace("\\n", "\n").encode()
        jwt_token = JWTAuthentication.get_the_token_from_header(jwt_token)

        try:
            payload = jwt.decode(jwt_token, public_key, settings.JWT_ALGORITHM)
        except ExpiredSignatureError:
            raise AuthenticationFailed({"detail": {"code": "TOKEN_EXPIRED", "message": "Токен устарел"}})
        except InvalidTokenError:
            raise AuthenticationFailed({"detail": {"code": "TOKEN_INCORRECT", "message": "Некорректный токен"}})

        user = User(id=22, username='someone')

        return user, payload.get('sub')


    # удаление заголовка 'Bearer' из токена
    @classmethod
    def get_the_token_from_header(cls, token):
        token = token.replace('Bearer', '').replace(' ', '')
        return token