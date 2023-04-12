from django.shortcuts import render
from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import *
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate, login, logout
import requests
from datetime import datetime, timedelta
import openai
import cryptocompare
## importing of the tensorflow modules

from keras.models import Sequential
from keras.layers import Dense
from keras.layers import LSTM

## importing all the libraries

## for working with the data frame
import pandas as pd
import numpy as np
from datetime import date
import yfinance as yf
import datetime as dt
## for visualizations
import matplotlib.pyplot as plt
import seaborn as sns
from openpyxl import load_workbook
import plotly.express as px
from plotly.offline import plot
import plotly.graph_objs as go

## for importing of the dataset
from alpha_vantage.timeseries import TimeSeries

## for training the model
import tensorflow as tf
import math
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error
from sklearn.metrics import accuracy_score

## for predicting the accuracy of the regression model
from sklearn.metrics import r2_score
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
def crypto_search(request):
    if request.user.is_authenticated:

        return render(request, 'crypto_search.html')
    else:
        messages.error(request, "Please log in first")
        return redirect('login')

@login_required(login_url='/login/')
def forex_search(request):
    if request.user.is_authenticated:

        return render(request, 'forex_search.html')
    else:
        messages.error(request, "Please log in first")
        return redirect('login')

@login_required(login_url='/login/')
def company_search(request):
    if request.user.is_authenticated:

        if request.method == 'POST':
            symbol = request.POST.get('symbol', '')
            type=request.POST.get('type', '')
            check = Portfolio.objects.filter(user=request.user, symbol=symbol)
            print(check)
            if len(check) != 0:
                remove = True
            else:
                remove = False
            if type == 'Crypto':
                try:
                    url = f'https://www.alphavantage.co/query?function=CURRENCY_EXCHANGE_RATE&from_currency={symbol}' \
                    '&to_currency=USD&apikey' \
                          '=THXW5Z2G9JZKTRK4'
                    r = requests.get(url)
                    data = r.json()
                    print(data)
                    symb=data['Realtime Currency Exchange Rate']['1. From_Currency Code']
                    name = data['Realtime Currency Exchange Rate']['2. From_Currency Name']
                    to_curr= data['Realtime Currency Exchange Rate']['3. To_Currency Code']
                    to_curr_name= data['Realtime Currency Exchange Rate']['4. To_Currency Name']
                    Exchange_Rate = data['Realtime Currency Exchange Rate']['5. Exchange Rate']
                    Last_Ref=data['Realtime Currency Exchange Rate']['6. Last Refreshed']
                    Bid = data['Realtime Currency Exchange Rate']['8. Bid Price']
                    Ask = data['Realtime Currency Exchange Rate']['9. Ask Price']

                    print(symb,name,to_curr,to_curr_name,Exchange_Rate,Last_Ref,Bid,Ask)
                    context={'symb':symb, 'name':name, 'to_curr':to_curr, 'to_curr_name':to_curr_name,
                    'Exchange_Rate':Exchange_Rate,'Last_Ref':Last_Ref,'Bid':Bid,'Ask':Ask,'remove':remove}
                    return render(request,'crypto_profile.html',context)


                except:
                    return render(request, 'no_result.html')

            if type == 'Forex':
                try:
                    url = f'https://www.alphavantage.co/query?function=CURRENCY_EXCHANGE_RATE&from_currency=' \
                    f'{symbol}&to_currency=INR&apikey=THXW5Z2G9JZKTRK4'

                    r = requests.get(url)
                    data = r.json()
                    print(data)
                    symb = data['Realtime Currency Exchange Rate']['1. From_Currency Code']
                    name = data['Realtime Currency Exchange Rate']['2. From_Currency Name']
                    to_curr = data['Realtime Currency Exchange Rate']['3. To_Currency Code']
                    to_curr_name = data['Realtime Currency Exchange Rate']['4. To_Currency Name']
                    Exchange_Rate = data['Realtime Currency Exchange Rate']['5. Exchange Rate']
                    Last_Ref = data['Realtime Currency Exchange Rate']['6. Last Refreshed']
                    Bid = data['Realtime Currency Exchange Rate']['8. Bid Price']
                    Ask = data['Realtime Currency Exchange Rate']['9. Ask Price']

                    print(symb, name, to_curr, to_curr_name, Exchange_Rate, Last_Ref, Bid, Ask)
                    context = {'symb': symb, 'name': name, 'to_curr': to_curr, 'to_curr_name': to_curr_name,
                               'Exchange_Rate': Exchange_Rate, 'Last_Ref': Last_Ref, 'Bid': Bid, 'Ask': Ask,
                               'remove': remove}
                    return render(request, 'forex_profile.html', context)


                except:
                    return render(request, 'no_result.html')

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

                print(remove)
                context={'symb':symb,'name':name,'desc':desc,'exchange':exchange,'currency':currency,'remove':remove,
                'type':type}
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
                check = Portfolio.objects.filter(user=request.user, symbol=symbol)
                print(check)
                if len(check) != 0:
                    remove = True
                else:
                    remove = False
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
               
                context={'symb':symb,'name':name,'list':list,'exchange':exchange,'currency':currency,'remove':remove}
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
            email = str(request.user.email)
            print(email)
            return render(request, 'portfolios.html',context)
    else:
        messages.error(request, "Please log in first")
        return redirect('login')



from .tasks import train_stock_model
@login_required(login_url='/login/')
def add_portfolio(request):
    if request.user.is_authenticated:

        if request.method == 'POST':
            symbol= request.POST['symbol']
            category= request.POST['category']
            email=str(request.user.email)
            args=str(str(symbol)+'&'+str(email))
            train_stock_model.delay(args)
            a=Portfolio.objects.create(user=request.user, symbol=symbol,category=category)
            a.save()
            messages.success(request, "Added to Portfolio..You will get an email once the ML model for this is created")

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

            a=Portfolio.objects.get(user=request.user, symbol=symbol)
            print("delete request running")
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


@login_required(login_url='/login/')
def daily_visualization(request,symb,option):
    if request.user.is_authenticated:
        symbol = symb
        API_key = 'I9OE24WDJWG30SN4'
        outputsize = 'compact'
        ts = TimeSeries(key=API_key, output_format='pandas')
        typ=option
        ## making the coditions
        if typ == 1: #daily
            state = ts.get_daily_adjusted(symbol, outputsize=outputsize)[0]
            basis='daily'
        elif typ == 2: #weekly
            state = ts.get_weekly_adjusted(symbol)[0]
            basis='weekly'
        elif typ == 3: #monthly
            state = ts.get_monthly_adjusted(symbol)[0]
            basis='monthly'
        elif typ == 4:

            state = ts.get_intraday(symbol, interval='1min', outputsize=outputsize)[0]
            basis ='interval of 1 min'
        elif typ == 5:

            state = ts.get_intraday(symbol, interval='5min', outputsize=outputsize)[0]
            basis = 'interval of 5 min'
        elif typ == 6:

            state = ts.get_intraday(symbol, interval='15min', outputsize=outputsize)[0]
            basis = 'interval of 15 min'
        elif typ == 7:

            state = ts.get_intraday(symbol, interval='30min', outputsize=outputsize)[0]
            basis = 'interval of 30 min'
        elif typ == 8:

            state = ts.get_intraday(symbol, interval='60min', outputsize=outputsize)[0]
            basis = 'interval of 60 min'
        else:
            print('Wrong Entry')
        ## displaying the dataset
        state.reset_index(inplace=True)
        print(state)
        ## graph for the opening price
        fig = px.line(state, x=state['date'], y=state['1. open'], title='Open price of the given stock')

        fig_div=plot(fig,output_type='div')
        ## graph for closing price
        fig2 = px.line(state, x=state['date'], y=state['4. close'], title='Close price of the given stock')

        fig2_div = plot(fig2, output_type='div')
        ## graph for Highest price of the portfolio
        fig3 = px.line(state, x=state['date'], y=state['2. high'], title='High price of the given stock')

        fig3_div = plot(fig3, output_type='div')

        """Financial Indicators"""
        ## finding the moving average
        ## moving average
        window = 50
        TS = state['4. close']

        ts_moving_avg = TS.rolling(window=window).mean()
        ## calculating the 50 days moving average of the given ticker

        state['Price'] = state['SMA_50'] = state['4. close'].rolling(window=50).mean()
        fig4 = px.line(state, x=state['date'], y=state['Price'], title='50-day SMA', labels={"50-dat SMA"})
        fig4.update_traces(line=dict(color='green'))
        fig4_div = plot(fig4, output_type='div')

        ## calculating the 200 day moving average of the given ticker
        state['Price'] = state['SMA_50'] = state['4. close'].rolling(window=200).mean()
        fig5 = px.line(state, x=state['date'], y=state['Price'], title='200-day SMA', labels={"200-dat SMA"})
        fig5.update_traces(line=dict(color='green'))
        fig5_div = plot(fig5, output_type='div')

        ## plotting the EXPONENTIAL MOVING AVERAGE GRAPH(EMA)

        state['Price'] = state['EMA_50'] = state['4. close'].ewm(span=50, adjust=False).mean()
        fig6 = px.line(state, x=state['date'], y=state['Price'], title='50-day EMA', labels={"50-dat EMA"})
        fig6.update_traces(line=dict(color='red'))
        fig6_div = plot(fig6, output_type='div')

        ## making the candlestick chart
        fig7 = go.Figure(data=[go.Candlestick(x=state['date'],
                                             open=state['1. open'],
                                             high=state['2. high'],
                                             low=state['3. low'],
                                             close=state['4. close'])])
        fig7_div = plot(fig7, output_type='div')

        context={'symb': symbol,'option':option,'fig':fig_div,'fig2':fig2_div,'fig3':fig3_div,'basis':basis,
        'fig4':fig4_div,'fig5':fig5_div,'fig6':fig6_div,'fig7':fig7_div,}
        return render(request, 'visualization.html',context)




    else:
        messages.error(request, "Please log in first")
        return redirect('login')


@login_required(login_url='/login/')
def btc_visualization(request,symb,option):
    if request.user.is_authenticated:
        symbol = symb
        API_key = 'I9OE24WDJWG30SN4'
        outputsize = 'compact'
        ts = TimeSeries(key=API_key, output_format='pandas')
        typ=option
        ## making the coditions
        if typ == 1: #daily
            state = ts.get_daily_adjusted(symbol, outputsize=outputsize)[0]
            basis='daily'
        elif typ == 2: #weekly
            state = ts.get_weekly_adjusted(symbol)[0]
            basis='weekly'
        elif typ == 3: #monthly
            state = ts.get_monthly_adjusted(symbol)[0]
            basis='monthly'
        elif typ == 4:

            state = ts.get_intraday(symbol, interval='1min', outputsize=outputsize)[0]
            basis ='interval of 1 min'
        elif typ == 5:

            state = ts.get_intraday(symbol, interval='5min', outputsize=outputsize)[0]
            basis = 'interval of 5 min'
        elif typ == 6:

            state = ts.get_intraday(symbol, interval='15min', outputsize=outputsize)[0]
            basis = 'interval of 15 min'
        elif typ == 7:

            state = ts.get_intraday(symbol, interval='30min', outputsize=outputsize)[0]
            basis = 'interval of 30 min'
        elif typ == 8:

            state = ts.get_intraday(symbol, interval='60min', outputsize=outputsize)[0]
            basis = 'interval of 60 min'
        else:
            print('Wrong Entry')
        ## displaying the dataset
        state.reset_index(inplace=True)
        print(state)
        ## graph for the opening price
        fig = px.line(state, x=state['date'], y=state['1. open'], title='Open price of the given stock')

        fig_div=plot(fig,output_type='div')
        ## graph for closing price
        fig2 = px.line(state, x=state['date'], y=state['4. close'], title='Close price of the given stock')

        fig2_div = plot(fig2, output_type='div')
        ## graph for Highest price of the portfolio
        fig3 = px.line(state, x=state['date'], y=state['2. high'], title='High price of the given stock')

        fig3_div = plot(fig3, output_type='div')

        """Financial Indicators"""
        ## finding the moving average
        ## moving average
        window = 50
        TS = state['4. close']

        ts_moving_avg = TS.rolling(window=window).mean()
        ## calculating the 50 days moving average of the given ticker

        state['Price'] = state['SMA_50'] = state['4. close'].rolling(window=50).mean()
        fig4 = px.line(state, x=state['date'], y=state['Price'], title='50-day SMA', labels={"50-dat SMA"})
        fig4.update_traces(line=dict(color='green'))
        fig4_div = plot(fig4, output_type='div')

        ## calculating the 200 day moving average of the given ticker
        state['Price'] = state['SMA_50'] = state['4. close'].rolling(window=200).mean()
        fig5 = px.line(state, x=state['date'], y=state['Price'], title='200-day SMA', labels={"200-dat SMA"})
        fig5.update_traces(line=dict(color='green'))
        fig5_div = plot(fig5, output_type='div')

        ## plotting the EXPONENTIAL MOVING AVERAGE GRAPH(EMA)

        state['Price'] = state['EMA_50'] = state['4. close'].ewm(span=50, adjust=False).mean()
        fig6 = px.line(state, x=state['date'], y=state['Price'], title='50-day EMA', labels={"50-dat EMA"})
        fig6.update_traces(line=dict(color='red'))
        fig6_div = plot(fig6, output_type='div')

        ## making the candlestick chart
        fig7 = go.Figure(data=[go.Candlestick(x=state['date'],
                                             open=state['1. open'],
                                             high=state['2. high'],
                                             low=state['3. low'],
                                             close=state['4. close'])])
        fig7_div = plot(fig7, output_type='div')

        context={'symb': symbol,'option':option,'fig':fig_div,'fig2':fig2_div,'fig3':fig3_div,'basis':basis,
        'fig4':fig4_div,'fig5':fig5_div,'fig6':fig6_div,'fig7':fig7_div,}
        return render(request, 'visualization.html',context)




    else:
        messages.error(request, "Please log in first")
        return redirect('login')


@login_required(login_url='/login/')
def crypto_visualization(request,symb):
    if request.user.is_authenticated:
        symbol = symb
        param=f"{symbol}-USD"
        param2 = f"{symbol}_USD"
        start = dt.datetime(2019, 1, 1)
        end = dt.datetime.now()
        btc = yf.download(param, start, end)
        print(btc.head)
        btc = btc.drop(['Open', 'High', 'Low', 'Volume', 'Adj Close'], axis=1)  # dropping extra columns
        # Modify Data Frame
        btc.reset_index(inplace=True)  # moves the date column to its own index
        btc = btc.rename(columns={'Close': param2})  # renaming Close to BTC_USD
        btc['SMA_2YR'] = btc[param2].rolling(730, min_periods=1).mean()  # creating a 2 year Simple Moving Averages
        btc['SMA_4YR'] = btc[param2].rolling(1460, min_periods=1).mean()  # creating a 4 year Simple Moving Averages
        fig1 = px.line(btc, x='Date', y=param2, log_y=True,
                       title='<b>PRICE VISUALIZATION<b>', color_discrete_sequence=["darkorange"])
        fig1_div = plot(fig1, output_type='div')
        fig2 = px.line(btc, x='Date', y='SMA_2YR', log_y=True,
                       title='<b>PRICE VISUALIZATION: 2 YEAR SIMPLE MOVING AVERAGES<b>',
                       color_discrete_sequence=["forestgreen"])
        fig2_div = plot(fig2, output_type='div')
        fig3 = px.line(btc, x='Date', y='SMA_4YR', log_y=True,
                       title='<b>PRICE VISUALIZATION: 4 YEAR SIMPLE MOVING AVERAGES<b>',
                       color_discrete_sequence=["blue"])
        fig3_div = plot(fig3, output_type='div')
        fig4 = px.line(btc, x='Date', y=[param2, 'SMA_4YR', 'SMA_2YR'], log_y=True,
                       title='<b>PRICE VISUALIZATION : COMBINED GRAPH<b>',
                       color_discrete_sequence=["darkorange", "blue", "forestgreen"])
        fig4_div = plot(fig4, output_type='div')
        context = {'symb': symbol, 'fig1': fig1_div, 'fig2': fig2_div, 'fig3': fig3_div,
                   'fig4': fig4_div,}
        return render(request, 'crypto_visualization.html', context)




    else:
        messages.error(request, "Please log in first")
        return redirect('login')



@login_required(login_url='/login/')
@csrf_exempt
def get_price(request):
    if request.method == 'POST':
        symb = request.POST.get('symb')
        print(symb)
        # fetching the realtime price of Bitcoin
        x=datetime.now()
        y=cryptocompare.get_price(symb, 'USD')[symb]['USD']
        return JsonResponse({'x':x, 'y':y})
    else:
        return render(request, 'error404.html')

@login_required(login_url='/login/')
def forex(request):
    if request.user.is_authenticated:

        if request.method == 'POST':
            symbol = request.POST['symbol']

            try:
                check = Portfolio.objects.filter(user=request.user, symbol=symbol)
                print(check)
                if len(check) != 0:
                    remove = True
                else:
                    remove = False
                url = f'https://www.alphavantage.co/query?function=CURRENCY_EXCHANGE_RATE&from_currency=' \
                      f'{symbol}&to_currency=INR&apikey=THXW5Z2G9JZKTRK4'

                r = requests.get(url)
                data = r.json()
                print(data)
                symb = data['Realtime Currency Exchange Rate']['1. From_Currency Code']
                name = data['Realtime Currency Exchange Rate']['2. From_Currency Name']
                to_curr = data['Realtime Currency Exchange Rate']['3. To_Currency Code']
                to_curr_name = data['Realtime Currency Exchange Rate']['4. To_Currency Name']
                Exchange_Rate = data['Realtime Currency Exchange Rate']['5. Exchange Rate']
                Last_Ref = data['Realtime Currency Exchange Rate']['6. Last Refreshed']
                Bid = data['Realtime Currency Exchange Rate']['8. Bid Price']
                Ask = data['Realtime Currency Exchange Rate']['9. Ask Price']

                print(symb, name, to_curr, to_curr_name, Exchange_Rate, Last_Ref, Bid, Ask)
                context = {'symb': symb, 'name': name, 'to_curr': to_curr, 'to_curr_name': to_curr_name,
                           'Exchange_Rate': Exchange_Rate, 'Last_Ref': Last_Ref, 'Bid': Bid, 'Ask': Ask,
                           'remove': remove}


                return render(request, 'forex.html', context)
            except:
                return render(request, 'no_result.html')

        else:
            return render(request, 'error404.html')
    else:
        messages.error(request, "Please log in first")
        return redirect('login')

from alpha_vantage.foreignexchange import ForeignExchange
def forex_visualization(request):
    if request.user.is_authenticated:

        if request.method == 'POST':
            symbol = request.POST['symbol']
            curr_to=request.POST['curr_to']
            typ = request.POST.get('type', '')


            try:
                check = Portfolio.objects.filter(user=request.user, symbol=symbol)

                if len(check) != 0:
                    remove = True
                else:
                    remove = False
                url = f'https://www.alphavantage.co/query?function=CURRENCY_EXCHANGE_RATE&from_currency=' \
                      f'{symbol}&to_currency=INR&apikey=THXW5Z2G9JZKTRK4'

                r = requests.get(url)
                data = r.json()

                symb = data['Realtime Currency Exchange Rate']['1. From_Currency Code']
                name = data['Realtime Currency Exchange Rate']['2. From_Currency Name']
                to_curr = data['Realtime Currency Exchange Rate']['3. To_Currency Code']
                to_curr_name = data['Realtime Currency Exchange Rate']['4. To_Currency Name']
                Exchange_Rate = data['Realtime Currency Exchange Rate']['5. Exchange Rate']
                Last_Ref = data['Realtime Currency Exchange Rate']['6. Last Refreshed']
                Bid = data['Realtime Currency Exchange Rate']['8. Bid Price']
                Ask = data['Realtime Currency Exchange Rate']['9. Ask Price']

                API_key = 'AZ2W0WRLXT67UV3V'

                outputsize = 'compact'
                from_symbol = symbol
                to_symbol = curr_to

                fe = ForeignExchange(key=API_key, output_format='pandas')
                ## making the conditions

                if typ == 'daily':
                    state = fe.get_currency_exchange_daily(from_symbol, to_symbol, outputsize=outputsize)[0]
                elif typ == 'weekly':
                    state = fe.get_currency_exchange_weekly(from_symbol, to_symbol)[0]
                elif typ == 'monthly':
                    state = fe.get_currency_exchange_monthly(from_symbol, to_symbol)[0]

                ## displaying the dataset
                state.reset_index(inplace=True)

                ## graph for the opening price
                fig = px.line(state, x=state['date'], y=state['1. open'], title='Open price of the given forex')
                fig_div = plot(fig, output_type='div')

                ## graph for closing price
                fig2 = px.line(state, x=state['date'], y=state['4. close'], title='Close price of the given forex')
                fig2_div = plot(fig2, output_type='div')

                ## graph for Highest price
                fig3 = px.line(state, x=state['date'], y=state['2. high'], title='High price of the given forex')
                fig3_div = plot(fig3, output_type='div')

                ## finding the moving average
                ## moving average
                window = 50
                FE = state['4. close']

                fe_moving_avg = FE.rolling(window=window).mean()

                ## calculating the 50 days moving average of the given ticker

                state['Price'] = state['SMA_50'] = state['4. close'].rolling(window=50).mean()
                fig4 = px.line(state, x=state['date'], y=state['Price'], title='50-day SMA', labels={"50-dat SMA"})
                fig4.update_traces(line=dict(color='red'))
                fig4_div = plot(fig4, output_type='div')

                ## calculating the 75 day moving average of the given ticker
                state['Price'] = state['SMA_50'] = state['4. close'].rolling(window=75).mean()
                fig5 = px.line(state, x=state['date'], y=state['Price'], title='75-day SMA', labels={"75-dat SMA"})
                fig5.update_traces(line=dict(color='red'))
                fig5_div = plot(fig5, output_type='div')

                ## plotting the EXPONENTIAL MOVING AVERAGE GRAPH(EMA)

                state['Price'] = state['EMA_50'] = state['4. close'].ewm(span=50, adjust=False).mean()
                fig6 = px.line(state, x=state['date'], y=state['Price'], title='50-day EMA', labels={"50-dat EMA"})
                fig6.update_traces(line=dict(color='red'))
                fig6_div = plot(fig6, output_type='div')

                ## making the candlestick chart
                fig7 = go.Figure(data=[go.Candlestick(x=state['date'],
                                                     open=state['1. open'],
                                                     high=state['2. high'],
                                                     low=state['3. low'],
                                                     close=state['4. close'])])
                fig7_div = plot(fig7, output_type='div')

                context = {'symb': symb, 'name': name, 'to_curr': to_curr, 'to_curr_name': to_curr_name,
                           'Exchange_Rate': Exchange_Rate, 'Last_Ref': Last_Ref, 'Bid': Bid, 'Ask': Ask,
                           'remove': remove,'curr_to':curr_to,'fig':fig_div,'fig2':fig2_div,'fig3':fig3_div,
        'fig4':fig4_div,'fig5':fig5_div,'fig6':fig6_div,'fig7':fig7_div,}

                return render(request, 'forex_visualization.html', context)
            except:
                return render(request, 'no_result.html')

        else:
            return render(request, 'error404.html')
    else:
        messages.error(request, "Please log in first")
        return redirect('login')


def create_dataset(dataset, time_step=1):
	dataX, dataY = [], []
	for i in range(len(dataset)-time_step-1):
		a = dataset[i:(i+time_step), 0]
		dataX.append(a)
		dataY.append(dataset[i + time_step, 0])
	return np.array(dataX), np.array(dataY)



def get_stock_model(symbol):
    stock_model = StockModel.objects.filter(symbol=symbol).first()
    model_text = stock_model.model
    model_json = json.loads(model_text)
    model = model_from_json(model_json)
    model.compile(loss='mean_squared_error', optimizer='adam')  # recompile the model before using it
    return model

from keras.models import model_from_json
@login_required(login_url='/login/')
def make_prediction(request,symb,cat):
    if request.user.is_authenticated:
        symbol=symb
        category=cat
        stock_model = StockModel.objects.filter(symbol=symbol).first()
        accuracy = stock_model.accuracy
        model=get_stock_model(symbol)
        API_key = '7N58ARN74RCCMY0L'

        outputsize = 'compact'

        typ = "weekly"
        ts = TimeSeries(key=API_key, output_format='pandas')
        state = ts.get_weekly_adjusted(symbol)[0]
        state.reset_index(inplace=True)
        ## taking the close values for the evaluation
        scaler = MinMaxScaler(feature_range=(0, 1))
        df = state.reset_index()['4. close']
        print(df)
        df = scaler.fit_transform(np.array(df).reshape(-1, 1))
        prediction=model.predict(df)

        prediction=scaler.inverse_transform(prediction)
        value=np.mean(prediction)

        #fig = px.line(prediction, x=state['date'], y=state['1. open'], title='Open price of the given forex')
        #fig_div = plot(fig, output_type='div')

        # Get the number of data points
        n_points = prediction.shape[0]

        # Create the plotly figure
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=np.arange(n_points), y=prediction[:, 0], mode='lines'))

        # Set the layout of the plot
        fig.update_layout(title='Predicted Closing Values ', xaxis_title='Index', yaxis_title='Data')

        # Show the plot
        fig_div = plot(fig, output_type='div')
        print(type(prediction))
        print(prediction.shape)
        context={'symbol':symbol,'category':category,'prediction':prediction,'accuracy':accuracy,'fig':fig_div,
        'value':value}
        return render(request, 'prediction.html', context)




    else:
        messages.error(request, "Please log in first")
        return redirect('login')
