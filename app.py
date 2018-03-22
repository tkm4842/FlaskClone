from flask import Flask, render_template, request, redirect
import quandl
import bokeh
from bokeh.plotting import figure, show
from bokeh.palettes import all_palettes
from bokeh.layouts import widgetbox
from bokeh.models.widgets import CheckboxGroup
from bokeh.io import output_notebook
from bokeh.embed import components
from bokeh.resources import INLINE
import numpy as np
import datetime as dt

import os
from os import environ

app = Flask(__name__)


# API key is set as config var in Heroku. To run locally, pull config vars from Heroku as .env file.
quandl.ApiConfig.api_key = os.environ['quandl_API_key']

# options 
price_type_list = ['open','close','adj_open','adj_close']
app.vars={}

def get_data(app_vars):
	ticker=app_vars['tickersymbol']

	columns =['date']
	for option in app_vars:
		if option!='tickersymbol' and app_vars[option]==1:
			columns.append(option)

	data =  quandl.get_table('WIKI/PRICES', paginate=True,qopts = { 'columns': columns}, date = { 'gte': '2018-03-01', 'lte': str(dt.datetime.now().strftime("%Y-%m-%d")) }, ticker=ticker)

	return data
	
def datetime(x):
    return np.array(x, dtype=np.datetime64)

def getcolordict(price_type_list):
	colormap = all_palettes['Viridis'][len(price_type_list)]
	colordict=dict()
	for i, price_type in enumerate(price_type_list):
		colordict[price_type] = colormap[i]
	return colordict

def create_figure(data, ticker):
	p=figure(x_axis_type='datetime', title='Quandl WIKI EOD Stock Prices')
	p.grid.grid_line_alpha=0.3
	p.xaxis.axis_label='Date'
	p.yaxis.axis_label='Stock Price'
	
	colordict= getcolordict(price_type_list)


	df = data
	for col in df.columns:
		if col!='date':
			p.line(x=datetime(df['date']), y=df[col], color=colordict[col], legend=ticker+': '+col)
	p.legend.location='top_left'
	return p


@app.route('/')
def hello():
    return redirect('/index')


@app.route('/index',methods=['GET','POST'])
def index():
	'''
	# Determine the selected option
	current_pricetype = request.args.get("pricetype")
	if current_pricetype == None:
		current_pricetype = price_type_list
	# Create the plot
	plot = create_figure(current_pricetype)
	
	
	# Embed plot into HTML via Flask Render
	script, div = components(plot)
	return render_template("quandlWIKIprice.html", script=script, div=div,
		price_type_list=price_type_list,  current_pricetype=current_pricetype)
	'''
	if request.method=='GET':
		return render_template('WIKIpriceinfo.html')
	else:
		# request was a post
		app.vars['tickersymbol'] = request.form['tickersymbol']


		for option in price_type_list:
			name = request.form.get(option)
			if name==None:
				app.vars[option]=0
			else:

				app.vars[option] = 1

		ticker = app.vars['tickersymbol']
		data = get_data(app.vars)
		p = create_figure(data, ticker)



		# Embed plot into HTML via Flask Render
		script, div = components(p)
		js_resources = INLINE.render_js()
		css_resources = INLINE.render_css()

		return render_template("end.html",  plot_script=script,  plot_div=div,js_resources=js_resources, css_resources=css_resources)






if __name__ == '__main__':


	app.run()

	'''
	app_vars={'tickersymbol': 'GOOG','open':1,'close':1,'adj_open':1,'adj_close':1}
	ticker = app_vars['tickersymbol']
	data = get_data(app_vars)
	print data
	p=create_figure(data, ticker)
	show(p)'''