"""
URL configuration for newproject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from spt import views_pages

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('spt.urls')),
    path('api-auth/', include('rest_framework.urls')),
    
    # Page views
    path('', views_pages.index, name='index'),
    path('products/', views_pages.products, name='products'),
    path('cart/', views_pages.cart, name='cart'),
    path('checkout/', views_pages.checkout, name='checkout'),
    path('order/<int:order_id>/', views_pages.order_tracking, name='order_tracking'),
    path('account/', views_pages.customer_account, name='account'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

