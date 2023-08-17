"""
URL configuration for mini_projet_django project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from django.urls import path

from mini_projet_equipement import views
from mini_projet_equipement.views import TeacherLoginView, TeacherLogoutView

urlpatterns = [
    path('admin/', admin.site.urls),

    path('login/', TeacherLoginView.as_view(), name='teacher_login'),
    path('logout/', TeacherLogoutView.as_view(), name='teacher_logout'),

    # Equipment App URLs
    path('equipments/', views.equipment_list, name='equipment_list'),
    path('equipments/<int:pk>/', views.equipment_detail, name='equipment_detail'),
    path('equipments/create/', views.equipment_create, name='equipment_create'),
    path('equipments/<int:pk>/update/', views.equipment_update, name='equipment_update'),
    path('equipments/<int:pk>/delete/', views.equipment_delete, name='equipment_delete'),


    path('teachers/', views.teacher_list, name='teacher_list'),
    path('teachers/<int:pk>/', views.teacher_detail, name='teacher_detail'),
    path('teachers/create/', views.teacher_create, name='teacher_create'),
    path('teachers/<int:pk>/update/', views.teacher_update, name='teacher_update'),
    path('teachers/<int:pk>/delete/', views.teacher_delete, name='teacher_delete'),

    path('accessories/', views.accessory_list, name='accessory_list'),
    path('accessories/<int:pk>/', views.accessory_detail, name='accessory_detail'),
    path('accessories/create/', views.accessory_create, name='accessory_create'),
    path('accessories/<int:pk>/update/', views.accessory_update, name='accessory_update'),
    path('accessories/<int:pk>/delete/', views.accessory_delete, name='accessory_delete'),

]
