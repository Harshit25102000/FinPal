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
from datetime import datetime, timedelta
import openai
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

        N_DAYS_AGO = 1

        today = datetime.now()
        n_days_ago = today - timedelta(days=N_DAYS_AGO)
        today = str(today)
        n_days_ago = str(n_days_ago)
        url = "https://contextualwebsearch-websearch-v1.p.rapidapi.com/api/search/NewsSearchAPI"

        querystring = {"q": "finance", "pageNumber": "1", "pageSize": "10", "autoCorrect": "true",
                       "fromPublishedDate": n_days_ago,
                       "toPublishedDate": today}

        headers = {
            "X-RapidAPI-Key": "5df3ca1e69msh48ca23362eb42e8p11e1fdjsn715f9fad8852",
            "X-RapidAPI-Host": "contextualwebsearch-websearch-v1.p.rapidapi.com"
        }

        response = requests.request("GET", url, headers=headers, params=querystring)

        a = response.json()
        z = a['value']
        out = z[0:8]

        context={'out':out}
        return render(request, 'user_home.html',context)
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
            symbol = request.POST.get('symbol', '')


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
                check = Portfolio.objects.filter(user=request.user, symbol=symbol)
                print(check)
                if len(check)!=0:
                    remove = True
                else:
                    remove = False
                print(remove)
                context={'symb':symb,'name':name,'desc':desc,'exchange':exchange,'currency':currency,'remove':remove}
                return render(request, 'company_profile.html',context)
            except:
                return render(request, 'no_result.html')

        else:
            return render(request, 'error404.html')
    else:
        messages.error(request, "Please log in first")
        return redirect('login')

@login_required(login_url='/login/')
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
               
                context={'symb':symb,'name':name,'list':list,'exchange':exchange,'currency':currency,}
                return render(request, 'fundamentals.html',context)
            except:
                return render(request, 'no_result.html')

        else:
            return render(request, 'error404.html')
    else:
        messages.error(request, "Please log in first")
        return redirect('login')

@login_required(login_url='/login/')
def portfolio(request):
    if request.user.is_authenticated:
        list=Portfolio.objects.filter(user=request.user)
        if len(list)==0:

            return render(request, 'empty_portfolio.html')
        else:
            context={'list':list}
            return render(request, 'portfolios.html',context)
    else:
        messages.error(request, "Please log in first")
        return redirect('login')

@login_required(login_url='/login/')
def add_portfolio(request):
    if request.user.is_authenticated:

        if request.method == 'POST':
            symbol= request.POST['symbol']

            a=Portfolio.objects.create(user=request.user, symbol=symbol)
            a.save()
            messages.success(request, "Added to Portfolio")
            return redirect('portfolio')


        else:
            return render(request, 'error404.html')
    else:
        messages.error(request, "Please log in first")
        return redirect('login')

@login_required(login_url='/login/')
def del_portfolio(request):
    if request.user.is_authenticated:

        if request.method == 'POST':
            symbol= request.POST['symbol']

            a=Portfolio.objects.filter(user=request.user, symbol=symbol).first()
            a.delete()
            messages.success(request, "Removed from Portfolio")
            return redirect('portfolio')


        else:
            return render(request, 'error404.html')
    else:
        messages.error(request, "Please log in first")
        return redirect('login')



def news(request):


        N_DAYS_AGO = 1

        today = datetime.now()
        n_days_ago = today - timedelta(days=N_DAYS_AGO)
        today = str(today)
        n_days_ago = str(n_days_ago)
        url = "https://contextualwebsearch-websearch-v1.p.rapidapi.com/api/search/NewsSearchAPI"

        querystring = {"q": "finance", "pageNumber": "1", "pageSize": "20", "autoCorrect": "true",
                       "fromPublishedDate": n_days_ago,
                       "toPublishedDate": today}

        headers = {
            "X-RapidAPI-Key": "5df3ca1e69msh48ca23362eb42e8p11e1fdjsn715f9fad8852",
            "X-RapidAPI-Host": "contextualwebsearch-websearch-v1.p.rapidapi.com"
        }

        response = requests.request("GET", url, headers=headers, params=querystring)

        a = response.json()
        z = a['value']


        context = {'out': z}
        if request.user.is_authenticated:
            return render(request, 'news.html', context)
        else:
            return render(request, 'news2.html', context)




@login_required(login_url='/login/')
def support(request):
    return render(request, 'support.html',)

@login_required(login_url='/login/')
def get_support(request):
    if request.method == 'POST':
        query = request.POST.get('query')
        openai.api_key = "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"
        a = openai.Completion.create(
            model="text-davinci-003",
            prompt=query,
            max_tokens=2048,
            temperature=0
        )
        ans=a['choices'][0]['text']
        return JsonResponse({'ans':ans})
    else:
        return render(request, 'error404.html')


@login_required(login_url='/login/')
def change_password(request):
    return render(request, 'change_password.html')

@login_required(login_url='/login/')
def handle_change_password(request):
    if request.method == 'POST':
        email = request.user
        password = request.POST['password']
        newpassword = request.POST['newpassword']
        newpassword2 = request.POST['newpassword2']

        user = authenticate(email=email, password=password)
        if user is not None:
            if newpassword != newpassword2:
                messages.error(request, "Passwords did not match")
                return redirect('change_password')
            else:
                u = User.objects.get(email=email)
                u.set_password(newpassword)
                u.save()
                messages.error(request, "Password changed successfully")
                return redirect('change_password')
        else:
            messages.error(request, "Invalid Credentials, Please try again")
            return redirect('change_password')




    else:
        return render(request, 'error404.html')
