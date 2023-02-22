from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import LoginForm, SignupForm
#from administration.views import administration
import folium, json
#from django.http import HttpResponse
from django.shortcuts import redirect
from parkings.views import generate_map, get_parkings

def user_logout(request):
    logout(request)
    return redirect('/')

def home(request):
    if request.user.is_authenticated:
        if request.user.is_superuser:
            return redirect('/administration')
        else:
            #read free_spaces and total_spaces from file park_1.txt inside media folder
            with open('media/park_1.txt', 'r') as f:
                free_spaces = int(f.readline())
                total_spaces = int(f.readline())
            park_status = str((total_spaces-free_spaces)) + '/' + str(total_spaces)
            park_percent = int(((total_spaces-free_spaces)/total_spaces)*100)
            context = {'park_status': park_status, 'park_percent': park_percent}
            return render(request, 'map.html', context)
            
    else: 
        messages.info(request,'HTTP ERROR: 401 - Unauthorized')
        return redirect('/')



def auth(request):
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
                    print("Invalid username or password.")
                    messages.error(request,"Invalid username/password.")
                    return render(request, 'login.html', context)
            else:
                messages.error(request,"Invalid username/password.")
                return render(request, 'login.html', context)

        elif 'signup' in request.POST:
            login_form = LoginForm()
            signup_form = SignupForm(request.POST)
            context = {'login_form': login_form, 'signup_form':signup_form}
            if signup_form.is_valid():
                signup_form.save()    
            else:
                messages.warning(request, 'Invalid input. Please try again.')
                
            return render(request, 'login.html', context)
    else:
        login_form = LoginForm()
        signup_form = SignupForm()
        context = {'login_form': login_form, 'signup_form': signup_form}
        return render(request, 'login.html', context)

# def test(request):
#     return render(request, 'index.html')
