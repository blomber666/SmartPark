from django.shortcuts import render
from map_tools import generate_map
from users import views as users_views

def park_1(request):
    print(request.user.is_authenticated)
    print(request.user)
    if request.user.is_authenticated:
        generate_map('parkings/static/park_1.json')
        return render(request,'park_1.html')
    else :
        users_views.home
# Create your views here.