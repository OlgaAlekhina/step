from django.apps import AppConfig


class ContestsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'contests'

    # регистрация OpenAPI схемы для кастомной аутентификации
    def ready(self):
        import contests.schema
