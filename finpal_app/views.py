from django.shortcuts import render
from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import *
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate, login, logout
import requests


def index(request):

    return render(request, 'index.html')

def signup_page(request):
    return render(request, 'signup.html')

def login_page(request):
    return render(request, 'login.html')

def handle_signup(request):

    if request.method == 'POST':

        email = request.POST['email']

        password1 = request.POST['password1']
        password2 = request.POST['password2']




        if password1 != password2:
            messages.error(request, 'Passwords do not match')
            return redirect('signup')

        if '@' not in email:
            messages.error(request, 'Enter a valid email address')
            return redirect('signup')


        user= User.objects.filter(email=email).first()

        if user:
            messages.error(request, 'Account already exists with this Email ')
            return redirect('signup')


        siteuser=User.objects.create_user(email,password1)

        siteuser.save()


        messages.success(request,"Account created successfully")
        login(request,siteuser)

        return redirect('user_home')

    else:
        return render(request, 'error404.html')

@login_required(login_url='/login/')
def user_home(request):
    if request.user.is_authenticated:

        return render(request, 'user_home.html')
    else:
        messages.error(request, "Please log in first")
        return redirect('login')

def handle_login(request):
    if request.method == 'POST':
        email= request.POST['email']
        password = request.POST['password']




        if '@' not in email:
            messages.error(request, 'Enter a valid email address')
            return redirect('login')
        look=User.objects.filter(email=email).filter()

        if len(look) ==0:
            messages.error(request, "Account does not exist")
            return redirect('login')

        user = authenticate(email=email, password=password)
        if user is not None:
            login(request, user)


            return redirect('user_home')
        else:
            messages.error(request,"Invalid Credentials, Please try again")
            return redirect('login')

    else:
        return render(request, 'error404.html')

def logout_view(request):
    logout(request)
    messages.success(request, 'You logged Out successfully')
    return redirect('Home')

@login_required(login_url='/login/')
def equity_search(request):
    if request.user.is_authenticated:

        return render(request, 'equity_search.html')
    else:
        messages.error(request, "Please log in first")
        return redirect('login')

@login_required(login_url='/login/')
def company_search(request):
    if request.user.is_authenticated:

        if request.method == 'POST':
            symbol= request.POST['symbol']


            try:
                url = f'https://www.alphavantage.co/query?function=OVERVIEW&symbol={symbol}&apikey=THXW5Z2G9JZKTRK4'
                r = requests.get(url)
                data = r.json()

                print(data)
                symb=data['Symbol']
                name=data['Name']
                desc=data['Description']
                exchange=data['Exchange']
                currency=data['Currency']
                context={'symb':symb,'name':name,'desc':desc,'exchange':exchange,'currency':currency}
                return render(request, 'company_profile.html',context)
            except:
                return render(request, 'no_result.html')

        else:
            return render(request, 'error404.html')
    else:
        messages.error(request, "Please log in first")
        return redirect('login')

def get_fundamentals(request):
    if request.user.is_authenticated:

        if request.method == 'POST':
            symbol= request.POST['symbol']


            try:
                url = f'https://www.alphavantage.co/query?function=OVERVIEW&symbol={symbol}&apikey=THXW5Z2G9JZKTRK4'
                r = requests.get(url)
                data = r.json()
                fund=data
                print(data)
                symb=data['Symbol']
                name=data['Name']
                del fund['Symbol']

                del fund["AssetType"]
                del fund["Name"]
                del fund["Description"]
                exchange=data['Exchange']
                currency=data['Currency']
                list=[(k, v) for k, v in fund.items()]

                context={'symb':symb,'name':name,'list':list,'exchange':exchange,'currency':currency}
                return render(request, 'fundamentals.html',context)
            except:
                return render(request, 'no_result.html')

        else:
            return render(request, 'error404.html')
    else:
        messages.error(request, "Please log in first")
        return redirect('login')







