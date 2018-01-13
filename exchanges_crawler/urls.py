from django.urls import path

from . import views

app_name = 'exchanges_crawler'
urlpatterns = [
    path('upd4Te', views.dev_update, name='update'),
    path('FIApd4Te', views.dev_fiat_update, name='fiat_update'),
]