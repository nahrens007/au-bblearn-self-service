from django.urls import path
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('update', views.update, name='update'),
]
