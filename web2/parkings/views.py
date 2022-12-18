from django.shortcuts import render
from map_tools import generate_map

def park_1(request):
    generate_map('web2/parkings/static/park_1.json')
    return render(request,'park_1.html')
# Create your views here.
