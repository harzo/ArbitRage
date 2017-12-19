from django.urls import path

from . import views

app_name = 'exchanges_crawler'
urlpatterns = [
    path('upd4Te', views.dev_update, name='update'),
]