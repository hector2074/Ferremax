from django.shortcuts import render, redirect, get_object_or_404
from .models import Producto
from django.http import JsonResponse, HttpResponse
import requests
from django.shortcuts import redirect
import mercadopago
from django.conf import settings
import os 
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from rest_framework import viewsets
from .serializer import ProductoSerializer
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser
from .forms import CustomUserCreationForm

# Create your views here.

def index (request):
    productos = Producto.objects.all()
    data = {
        'productos': productos
    }
    return render(request, "index.html", data)

def iniciosesion(request):
    return render(request, "vistacliente.html")

def search_view(request):
    query = request.GET.get('query', '')
    if query:
        results = Producto.objects.filter(nombre_producto__icontains=query)
    else: 
        results = Producto.objects.none

    return render(request, 'search_results.html', {'results': results})

def obtener_tasa_conversion_de_clp(moneda_destino):
    api_key = "f4b8b0b92ab42e8171840fad"
    url = f"https://v6.exchangerate-api.com/v6/{api_key}/latest/CLP"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        tasa = data['conversion_rates'].get(moneda_destino.upper())
        if tasa:
            return tasa
        else:
            return None
    else:
        return None

def api_conversion_moneda(request):
    moneda_destino = request.GET.get('moneda', 'USD').upper()
    tasa = obtener_tasa_conversion_de_clp(moneda_destino)
    if tasa is not None:
        return JsonResponse({'tasa_conversion': tasa})
    else:
        return JsonResponse({'error': 'Tasa de conversión no disponible'}, status=404)

def detalle_producto(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    moneda_destino = request.GET.get('moneda', 'USD').upper()  
    context = {'producto': producto}

    
    try:
        tasa_conversion = obtener_tasa_conversion_de_clp(moneda_destino)
        precio_convertido = producto.precio * tasa_conversion
        context['precio_convertido'] = f"{precio_convertido:.2f} {moneda_destino}"
    except Exception as e:
        context['error'] = f"Error al obtener tasa de conversión: {e}"

   
    sdk = mercadopago.SDK(settings.MERCADOPAGO_ACCESS_TOKEN)
    preference_data = {
        "items": [
            {
                "title": producto.nombre_producto,
                "quantity": 1,
                "unit_price": float(producto.precio),
                "currency_id": "CLP"
            }
        ],
    }
    preference_response = sdk.preference().create(preference_data)
    context['preference_id'] = preference_response["response"]["id"]  
 
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        if 'error' in context:
            return JsonResponse({'error': context['error']}, status=500)
        return JsonResponse({'precio_convertido': context['precio_convertido']})
    

    return render(request, 'detail_product.html', context)



def payment_success(request):
    return HttpResponse("Pago realizado con éxito.")

def payment_failure(request):
    return HttpResponse("Pago fallido.")

def payment_pending(request):
    
    return HttpResponse("Pago pendiente.")


def user_login(request):
    form = AuthenticationForm()  
    
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                
    # Obtener los productos y enviarlos al template
    productos = Producto.objects.all()
    return render(request, 'index.html', {'form': form, 'productos': productos})


def user_logout(request):
    logout(request)
    return redirect('index')


def register_user(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST) 
        if form.is_valid():
            form.save()
            return redirect('login') 
    else:
        form = UserCreationForm() 
    return render(request, 'register.html', {'form': form})

def dashboard_view(request):
    if not request.user.is_authenticated:
        return redirect('index') 
    if request.user.tipo_usuario == 'cliente':
        return redirect('index') 
    elif request.user.tipo_usuario == 'vendedor':
        return render(request, 'vendedor.html')
    elif request.user.tipo_usuario == 'bodeguero':
        return render(request, 'bodeguero.html')
    elif request.user.tipo_usuario == 'contador':
        return render(request, 'contador.html')
    
    return redirect('index') 

#API 

class ProductoViewSet(viewsets.ModelViewSet):
    queryset=Producto.objects.all()
    serializer_class = ProductoSerializer
    
    

    
class ListarProductos(APIView):
    def get(self, request):
        productos = Producto.objects.all()
        serializer = ProductoSerializer(productos, many=True)
        # Renderizamos el template para propósitos de visualización
        rendered_template = render(request, 'listarproductos.html', {'productos': serializer.data})
        # Devolvemos la respuesta JSON
        return Response(serializer.data)
    
class ListarProductosHTML(APIView):
    def get(self, request):
        productos = Producto.objects.all()
        serializer = ProductoSerializer(productos, many=True)
        return render(request, 'listarproductos.html', {'productos': serializer.data})
    
# Vista para el bodeguero
def bodeguero_view(request):
    # Obtener todos los productos
    productos = Producto.objects.all()
    return render(request, 'bodeguero.html', {'productos': productos})



def eliminar_stock(request, producto_id):
    if request.method == 'POST':
        try:
            producto = Producto.objects.get(id_producto=producto_id)
            producto.save()
            return JsonResponse({'success': True})
        except Producto.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Producto no encontrado'})
    else:
        return JsonResponse({'success': False, 'error': 'Método no permitido'})
    
    
def register_user(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            # Aquí podrías redirigir al usuario a otra página después del registro
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/register.html', {'form': form})