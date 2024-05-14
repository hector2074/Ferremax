from django.urls import path, include
from rest_framework import routers
from . import views


router=routers.DefaultRouter()
router.register(r'Producto', views.ProductoViewSet)

urlpatterns = [
    path('', views.index, name='index'),
    path('iniciosesion/', views.iniciosesion),
    path('search/', views.search_view, name='search_results'),
    path('producto/<int:pk>', views.detalle_producto, name="detalle_producto"),
    path('api/conversion/', views.api_conversion_moneda, name='api_conversion_moneda'),
    path('payment-success/', views.payment_success, name='payment-success'),
    path('payment-failure/', views.payment_failure, name='payment-failure'),
    path('payment-pending/', views.payment_pending, name='payment-pending'),
    path('login/', views.user_login, name='login'),
    path('accounts/profile/', views.user_login, name='profile'),
    path('logout/', views.user_logout, name='logout'),
    path('register/', views.register_user, name='register'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('', include(router.urls)),
    path('bodeguero/', views.bodeguero_view, name='bodeguero'),
    path('api/listar-productos/', views.ListarProductos.as_view(), name='listar_productos'),
    path('listar-productos/', views.ListarProductosHTML.as_view(), name='listar_productos_html'),
]
