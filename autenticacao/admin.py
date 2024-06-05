from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import AcessoCasa, Casa
class AcessoCasaInline(admin.TabularInline):
    model = AcessoCasa
    extra = 1  # Permite adicionar um novo campo vazio para preenchimento

class UserAdmin(BaseUserAdmin):
    inlines = (AcessoCasaInline,)

# Re-registra o User admin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

admin.site.register(Casa)