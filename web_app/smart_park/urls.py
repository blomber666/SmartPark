"""smart_park URL Configuration

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
from django.contrib import admin
from django.urls import path, include
from users import views as users_views
from parkings import views as parkings_views
from administration import views as admin_views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("__reload__/", include("django_browser_reload.urls")),
    path('admin/', admin.site.urls),
    path('', users_views.home, name='login'),
    path('logout/', users_views.user_logout, name='logout'),
    path('home/', users_views.map_view, name='home'),
    path('park_1/', parkings_views.park_1, name='park_1'),
    path('park_1/pay/', parkings_views.pay, name='pay'),
    path('administration/', admin_views.administration, name='administration'),
    path('administration/filter/', admin_views.filter, name='filter'),
    path('administration/override/', admin_views.override, name='override'),
    path('administration/price/', admin_views.price, name='price'),
    #API
    path('administration/state/<str:door>/', admin_views.get_door_state, name='get_door_state'),
    path('update_parkings/', parkings_views.get_parkings, name='get_parkings'),
    path('update_price/?P<str:start>', parkings_views.calculate_amount, name='get_price'),

]+ static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)