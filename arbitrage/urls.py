"""arbitrage URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
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
from django.urls import include, path
from exchanges import views as exchanges_views
from exchanges import views_apis as exchanges_apis

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('overview.urls')),
    path('spreads/', exchanges_views.spreads, name="spreads"),
    path('spreads/<left>/<right>', exchanges_views.spreads, name="spreads"),
    path('calculator/', exchanges_views.calculator, name="calculator"),
    path('calculator/<exchange>/', exchanges_views.calculator, name="calculator"),
    path('calculator/<exchange>/<left>/<right>', exchanges_views.calculator, name="calculator"),
    path('calculator/math/buy_amount_volume/', exchanges_apis.calculate_buy_amount_volume),
    path('update/', include('exchanges_crawler.urls')),
]
