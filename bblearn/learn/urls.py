from django.urls import path
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('courses',views.courses, name='courses'),
    path('viewUsers',views.viewUsers, name='viewUsers'),
    path('addUsers',views.addUsers, name='addUsers'),
]
