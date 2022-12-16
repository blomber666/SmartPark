from django.shortcuts import render


from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib import messages
from .forms import LoginForm, SignupForm

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
                print("useris none?")
                print(user is None)
                if user is not None:
                    login(request, user)
                    messages.info(request, f"You are now logged in as {username}.")
                    return render(request, 'test.html', context)
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