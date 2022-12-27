"""web_django URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
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
from django.contrib import admin, auth
from django.urls import path
#from web_django import views
from users import views as users_views
from parkings import views as park_views
from administration import views as admin_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', users_views.home, name='login'),
    path('logout/', users_views.user_logout, name='logout'),
    path('home/', users_views.map_view, name='home'),
    path('park_1/', park_views.park_1, name='park_1'),
    path('park_1/pay/', park_views.pay, name='pay'),
    path('administration/', admin_views.administration, name='administration')
]
