from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import EmailUserCreationForm

def register(request):
    """Handle user registration"""
    if request.method == 'POST':
        form = EmailUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            email = form.cleaned_data.get('email')
            messages.success(request, f'Account created for {email}! You can now log in.')
            return redirect('login')
    else:
        form = EmailUserCreationForm()
    return render(request, 'repository/register.html', {'form': form})

def user_login(request):
    """Handle user login"""
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            
            # Try to authenticate with username first
            user = authenticate(request, username=username, password=password)
            
            # If that fails, try to find a user with that email
            if user is None:
                from django.contrib.auth.models import User
                try:
                    user_obj = User.objects.get(email=username)
                    user = authenticate(request, username=user_obj.username, password=password)
                except User.DoesNotExist:
                    pass
            
            if user is not None:
                login(request, user)
                messages.info(request, f'You are now logged in as {user.username}.')
                return redirect('home')
            else:
                messages.error(request, 'Invalid username/email or password.')
        else:
            messages.error(request, 'Invalid username/email or password.')
    else:
        form = AuthenticationForm()
    return render(request, 'repository/login.html', {'form': form})

@login_required
def user_logout(request):
    """Handle user logout"""
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('home')