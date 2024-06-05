from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from vencimento.models import Casa

class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    casa = models.ForeignKey(Casa, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f'Perfil de {self.user.username}'

class AcessoCasa(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='acessos_casa')
    casa = models.ForeignKey(Casa, on_delete=models.CASCADE, related_name='usuarios_acesso')
    pode_acessar = models.BooleanField(default=True)

    class Meta:
        unique_together = ('usuario', 'casa')
        verbose_name = "Acesso à Casa"
        verbose_name_plural = "Acessos às Casas"

    def __str__(self):
        return f'{self.usuario.username} -> {self.casa.nome}'