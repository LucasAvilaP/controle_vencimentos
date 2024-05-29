from django.conf import settings
from django.db import models
from vencimento.models import Casa

class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    casa = models.ForeignKey(Casa, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f'Perfil de {self.user.username}'
