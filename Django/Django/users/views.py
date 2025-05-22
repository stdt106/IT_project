from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import RegisterUserForm
from django.contrib.auth.views import LoginView
from django.contrib.auth import logout, get_backends
from django.shortcuts import redirect


def custom_logout(request):
    logout(request)
    return redirect('/')


class CustomLoginView(LoginView):
    template_name = 'users/login.html'


def register(request):
    if request.method == 'POST':
        form = RegisterUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.backend = get_backends()[0].__module__ + "." + get_backends()[0].__class__.__name__
            login(request, user)
            return redirect('/')
    else:
        form = RegisterUserForm()
    return render(request, 'users/register.html', {'form': form})
