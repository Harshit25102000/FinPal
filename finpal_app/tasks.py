import json
import requests
from celery import shared_task
from django.core.mail import send_mail
from django.core import mail
from django.core import serializers
from .models import *
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
from django.core import serializers
from .models import *


def serialize_model(model):
    return json.dumps(serializers.serialize('json', [model])[0]['fields'])

def create_dataset(dataset, time_step=1):
	dataX, dataY = [], []
	for i in range(len(dataset)-time_step-1):
		a = dataset[i:(i+time_step), 0]   ###i=0, 0,1,2,3-----99   100
		dataX.append(a)
		dataY.append(dataset[i + time_step, 0])
	return np.array(dataX), np.array(dataY)


@shared_task(bind=True)
def train_stock_model(self,args):
    print("-------------------------------task running---------------------------------------------\n")
    my_string = args
    split_string = my_string.split('&', 1)
    symb = split_string[0]
    email = split_string[1] if len(split_string) > 1 else ""
    print(email)
    API_key = '7N58ARN74RCCMY0L'

    outputsize = 'compact'
    symbol = symb
    typ = "weekly"
    ts = TimeSeries(key=API_key, output_format='pandas')
    state = ts.get_weekly_adjusted(symbol)[0]
    state.reset_index(inplace=True)
    ## taking the close values for the evaluation

    df = state.reset_index()['4. close']
    print(df)
    # fig = px.line(state, x=state['date'], y=state['1. open'], title='Open price of the given forex')
    # fig_div = plot(fig, output_type='div')
    scaler = MinMaxScaler(feature_range=(0, 1))
    df = scaler.fit_transform(np.array(df).reshape(-1, 1))
    ## splitting of the dataset
    training_size = int(len(df) * 0.65)
    test_size = len(df) - training_size
    train_data, test_data = df[0:training_size, :], df[training_size:len(df), :1]
    time_step = 100
    X_train, y_train = create_dataset(train_data, time_step)
    X_test, ytest = create_dataset(test_data, time_step)
    # reshape input to be [samples, time steps, features] which is required for LSTM
    X_train = X_train.reshape(X_train.shape[0], X_train.shape[1], 1)
    X_test = X_test.reshape(X_test.shape[0], X_test.shape[1], 1)
    model = Sequential()
    model.add(LSTM(50, return_sequences=True, input_shape=(100, 1)))
    model.add(LSTM(50, return_sequences=True))
    model.add(LSTM(50))
    model.add(Dense(1))
    model.compile(loss='mean_squared_error', optimizer='adam')
    ## fitting the model
    model.fit(X_train, y_train, validation_data=(X_test, ytest), epochs=30, batch_size=64, verbose=1)
    X_train_prediction = model.predict(X_train)
    ## calculating the r2 score for the LSTM model
    training_data_accuracy = r2_score(y_train, X_train_prediction)
    accuracy=training_data_accuracy*100
    json_model=model.to_json()
    model_text = json.dumps(json_model)
    stock_model=StockModel.objects.create(symbol=symb,accuracy=accuracy,model=model_text)
    stock_model.save()
    stock_model=StockModel.objects.filter(symbol=symb).first()
    time=stock_model.created_at
    accuracy=stock_model.accuracy
    message=f"Woohoo your Machine Learning model for {symb} has been created successfully and saved to your account at {time} with an accuracy of {accuracy}% and it is now available to use."
    print(email)

    results=send_mail(
        'Your ML Model is Created',
        message,
        'harshit25102000@gmail.com',
        [email],
        fail_silently=False,
    )
    print(results)
    print("task ended")

