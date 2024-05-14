from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Producto, CustomUser, Categoria_Producto, Ferretería
# Register your models here.

class CustomUserAdmin(BaseUserAdmin):
    model = CustomUser
    list_display = ['username', 'email', 'tipo_usuario', 'is_staff', 'is_active']

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Producto)
admin.site.register(Categoria_Producto)
admin.site.register(Ferretería)
