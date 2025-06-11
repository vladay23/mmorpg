from django.apps import AppConfig

class ApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api'
    verbose_name = 'API для MMORPG проекта'

#from django.apps import AppConfig

#class ApiConfig(AppConfig):
 #   name = 'api'
#
#    def ready(self):
 #       import api.signals  # импортируем сигналы при запуске