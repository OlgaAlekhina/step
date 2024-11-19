from drf_spectacular.extensions import OpenApiAuthenticationExtension


# OpenAPI схема для кастомной аутентификации через JWT токены
class MyAuthenticationScheme(OpenApiAuthenticationExtension):
    target_class = 'contests.authentication.JWTAuthentication'
    name = 'JWTAuthentication'

    def get_security_definition(self, auto_schema):
        return {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }