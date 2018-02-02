from django.urls import path
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('viewUsers',views.viewUsers, name='viewUsers'),
    path('addUsers',views.addUsers, name='addUsers'),
    path('course', views.course, name='course'),
]
