from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
#from administration.views import administration
import folium
#from django.http import HttpResponse
from django.shortcuts import redirect


def test(request):    
    return render(request, 'tw_base.html')