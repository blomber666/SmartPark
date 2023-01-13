from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import LoginForm, SignupForm
#from administration.views import administration
import folium
#from django.http import HttpResponse
from django.shortcuts import redirect


def create_map():    
    map = folium.Map(location=[44.83895673644131, 11.614725304456822], zoom_start=15)

    folium.Marker(
        location = [44.8333320, 11.6166670],
        popup = "<a href=/park>Parking 1</a>", 
        icon = folium.Icon(color="darkpurple",icon="square-parking", prefix="fa")
        ).add_to(map)
    
    '''
    for i in range(len(f["attrazioni"])):
        folium.Marker(
            location = [f["attrazioni"][i]["x"],f["attrazioni"][i]["y"]],
            popup = "Parcheggio "+str(i),
            icon = folium.Icon(color="darkred", icon="map", prefix="fa")
            ).add_to(map)
    wexcel(tour, fun_name, iteration)
    route(tour)

    folium.GeoJson("percorso.geojson", name=fun_name).add_to(map)
    folium.LayerControl().add_to(map)
    
    for k in tour[0][1:-1]:
        folium.Marker(
            location = [f["attrazioni"][(k-1)]["x"],f["attrazioni"][(k-1)]["y"]],
            popup = f["attrazioni"][(k-1)]["nome"], 
            tooltip = tour[0].index(k),
            icon = folium.Icon(color="darkpurple",icon="square-parking", prefix="fa")
            ).add_to(map)
    '''

    map.save("parkings/templates/map.html")
    #wb.open(fun_name+"\\#"+str(iteration)+".html")
    del(map)



def user_logout(request):
    logout(request)
    return redirect('/')


def map_view(request):
    #if not os.path.exists("parkings/templates/map.html"): 
    #    create_map()
    if request.user.is_authenticated:
        if request.user.is_superuser:
            return redirect('/administration')
        else:
            return render(request, 'map.html', {})
    else: 
        messages.info(request,'HTTP ERROR: 401 - Unauthorized')
        return redirect('/')


def home(request):
    if request.user.is_authenticated:
        if request.user.is_superuser:
            return redirect('/administration')
        else:
            return redirect('/home')

    elif request.method == 'POST':

        if 'login' in request.POST:
            signup_form = SignupForm()
            login_form = LoginForm(request.POST, data=request.POST)
            context = {'login_form': login_form, 'signup_form':signup_form}
    
            if login_form.is_valid():
                username = login_form.cleaned_data.get('username')
                password = login_form.cleaned_data.get('password')
                user = authenticate(username=username, password=password)

                if user is not None:
                    
                    if user.is_superuser:
                        login(request, user)
                        return redirect('/administration')
                    else:
                        login(request, user)        
                        return redirect('/home')
                
                else:
                    messages.error(request,"Invalid username or password.")
                    return render(request, 'login.html', context)

        elif 'signup' in request.POST:
            login_form = LoginForm()
            signup_form = SignupForm(request.POST)
            context = {'login_form': login_form, 'signup_form':signup_form}
            if signup_form.is_valid():
                signup_form.save()
                messages.success(request, f'Your account has been created. You can log in now!')    
            else:
                messages.warning(request, f'Invalid input. Please try again.')
                
            return render(request, 'login.html', context)
    else:
        login_form = LoginForm()
        signup_form = SignupForm()
        context = {'login_form': login_form, 'signup_form': signup_form}
        return render(request, 'login.html', context)

