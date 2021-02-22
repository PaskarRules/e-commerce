from django.shortcuts import render, redirect

from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.core.mail import send_mail

from ecommerce import settings

from store.forms import *

def registerPage(request):
    if request.user.is_authenticated:
        return redirect('store')
    else:
        form = CreateUserForm()
        if request.method == 'POST':
            form = CreateUserForm(request.POST)
            if form.is_valid():
                user = form.save()
                username = form.cleaned_data.get('username')
                useremail = form.cleaned_data.get('email')

                Customer.objects.create(user=user, name=username, email=useremail)
                # send_mail(
                #     'New Account!', 'Thank you for register your account on our website!',
                #     settings.EMAIL_HOST_USER, [useremail], fail_silently=False
                # )
                # messages.success(request, 'Account was created for ' + username)

                return redirect('login')

        context = {'form': form}
        return render(request, 'accounts/register.html', context)


def loginPage(request):
    if request.user.is_authenticated:
        return redirect('store')
    else:
        if request.method == 'POST':
            username = request.POST.get('username')
            password = request.POST.get('password')

            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                return redirect('store')
            else:
                messages.info(request, 'Username OR password is incorrect')

        context = {}
        return render(request, 'accounts/login.html', context)


def logoutUser(request):
    logout(request)
    return redirect('store')