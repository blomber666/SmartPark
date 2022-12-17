from django.shortcuts import render
from django.contrib.auth import login, authenticate
from django.contrib import messages
from .forms import LoginForm, SignupForm
import folium, os

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

    map.save("web2/parkings/templates/map.html")
    #wb.open(fun_name+"\\#"+str(iteration)+".html")
    del(map)

def park(request):
    return render(request,'test.html')

def home(request):
    if request.method == 'POST':
        if 'login' in request.POST:
            signup_form = SignupForm()
            login_form = LoginForm(request.POST, data=request.POST)
            context = {'login_form': login_form, 'signup_form':signup_form}
            print("login form is valid?")
            print(login_form.is_valid())
            if login_form.is_valid():
                username = login_form.cleaned_data.get('username')
                password = login_form.cleaned_data.get('password')
                user = authenticate(username=username, password=password)
                print("user is none?")
                print(user is None)
                if user is not None:
                    login(request, user)
                    messages.info(request, f"You are now logged in as {username}.")
                    if not os.path.exists("web2/parkings/templates/map.html"): 
                        create_map()
                    return render(request, 'map.html', context)
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