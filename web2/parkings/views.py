from django.shortcuts import render
from map_tools import generate_map

def parkings(request):
    generate_map('parkings/static/park_1.json')
    return render(request,'map2.html')
# Create your views here.
