# api/signals.py

from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from django.db.models.signals import post_save

def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)

# подключение сигнала к модели User
post_save.connect(create_auth_token, sender=User)