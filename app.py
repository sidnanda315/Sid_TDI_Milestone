from flask import Flask, render_template, request, abort, redirect, url_for
import calendar
import datetime as dt
from datetime import date, timedelta
import requests, os
import pandas as pd
from urllib.request import Request, urlopen
import json
import pandas as pd
from pandas.io.json import json_normalize
from bokeh.plotting import figure, output_file, show
from bokeh.embed import components



def fetchData(stock):

    ######key = os.environ.get('API_KEY')
    key = 'QWBTYF47PT4KTIJ5'
    urlNparameters = 'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol=' + stock + '&outputsize=full&apikey=key'
    print(urlNparameters)
    r = requests.get(urlNparameters)
    stock_dict = r.json()
    df = pd.DataFrame.from_dict(stock_dict["Time Series (Daily)"], orient='index')
    df.drop(df.columns[[1, 2, 5, 6, 7]], axis=1, inplace=True)
    df = df.rename(columns={'1. open': 'open', '4. close': 'close', '5. adjusted close': 'adjusted close'})
    now = pd.to_datetime(dt.datetime.now().date())
    now = now.strftime("%Y-%m-%d")
    print('now=', now, type(now))
    one_month_before = dt.datetime.now() - dt.timedelta(days=30)
    one_month_before = one_month_before.strftime("%Y-%m-%d")
    print('now=', one_month_before, type(one_month_before))
    print('before loc', df.head())
    df = df.loc[now: one_month_before]
    df['Date'] = pd.to_datetime(df.index)
    df.reset_index(drop=True, inplace=True)
    df.columns = ['open', 'close', 'adjusted close', 'Date']
    df = df.sort_values(by=['Date'])
    df["adjusted open"] = (df["open"].astype(float)) / (1 + (
                (df["close"].astype(float) - df["adjusted close"].astype(float)) / df["adjusted close"].astype(float)))
    return df





def plotData(df2, price, stock2):
    #print('after getDataPlot1', df2.head())
    p = figure(
        width=1725,
        height=500,
        x_axis_type="datetime")
    if price == 'op':
        p.line(df2["Date"], df2["open"], line_width=3, color="red", alpha=0.5, legend_label="Opening Price")
    elif price == 'aop':
        p.line(df2["Date"], df2["adjusted open"], line_width=3, color="orange", alpha=0.5, legend_label="Adjusted Opening Price")
    elif price == 'cp':
        p.line(df2["Date"], df2["close"], line_width=3, color="blue", alpha=0.5, legend_label="Closing Price")
    elif price == 'acp':
        p.line(df2["Date"], df2["adjusted close"], line_width=3, color="green", alpha=0.5, legend_label="Adjusted_Closing Price")
    elif price == 'ap':
        p.line(df2["Date"], df2["open"], line_width=3, color="red", alpha=0.5, legend_label="Opening Price")
        p.line(df2["Date"], df2["close"], line_width=3, color="blue", alpha=0.5, legend_label="Closing Price")
        p.line(df2["Date"], df2["adjusted open"], line_width=3, color="orange", alpha=0.5, legend_label="Adjusted Opening price")
        p.line(df2["Date"], df2["adjusted close"], line_width=3, color="green", alpha=0.5, legend_label="Adjusted Closing Price")
    p.xaxis.axis_label = 'Date'
    p.legend.location = 'top_left'
    p.legend.title = 'Legend'
    p.legend.title_text_font = 'Arial'
    p.legend.title_text_font_size = '15pt'
    p.title.text = " Stock Price of " +stock2.upper() + " for the last month"
    p.title.align = "center"
    p.title.text_color = "blue"
    p.title.text_font_size = "25px"
    p.title.background_fill_color = "beige"
    script, div = components(p)
    #print(script)
    # output_file("plot.html")
    # show(p)
    return script, div




app = Flask(__name__)

@app.errorhandler(500)
def server_error(e):

    print('Please enter a valid ticker error')
    return render_template("WrongTicker.html")

@app.route('/WrongTicker', methods=['GET', 'POST'])
def back():
    if request.method== 'POST':
        return render_template("index.html")

@app.route('/About', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        return render_template("about.html")
    return render_template("about.html")

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method== 'POST':
        stock1 = request.form['stock']
        print(stock1)
        price1 = request.form['price']
        print (price1)
        df1 = fetchData(stock1)
        script, div = plotData(df1, price1, stock1)
        return render_template("plot.html", div=div, script=script)
    return render_template("index.html")

if __name__ == "__main__":
    app.run(port=44001)