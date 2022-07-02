from django.apps import AppConfig


class CheckApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'check_api'
    verbose_name = 'Сервис для генерации чеков'
