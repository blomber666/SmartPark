from django.shortcuts import render


from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from .forms import LoginForm, SignupForm

def home(request):
    if request.method == 'POST':
        print(request.POST)
        if 'login' in request.POST:
            signup_form = SignupForm()
            login_form = LoginForm(request.POST)
            context = {'form': login_form}
            print("logging in")
            return render(request, 'test.html', context)

        elif 'signup' in request.POST:
            login_form = LoginForm()
            signup_form = SignupForm(request.POST)
            context = {'login_form': login_form, 'signup_form':signup_form}
            if signup_form.is_valid():
                signup_form.save()
                messages.success(request, f'Your account has been created. You can log in now!')    
                return redirect('succesfully login')
            else:
                print(signup_form.errors)
                messages.warning(request, f'Invalid input. Please try again.')
                return render(request, 'login.html', context)
    else:
        login_form = LoginForm()
        signup_form = SignupForm()
        context = {'login_form': login_form, 'signup_form': signup_form}

    
    return render(request, 'login.html', context)