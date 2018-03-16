from flask import Flask, render_template, request, redirect
import quandl
import bokeh
from bokeh.plotting import figure, show
from bokeh.palettes import all_palettes
from bokeh.layouts import widgetbox
from bokeh.models.widgets import CheckboxGroup
from bokeh.io import output_notebook
import numpy as np


app = Flask(__name__)




# Set API key
quandl.ApiConfig.api_key = "sfvyrsyZzjsQaacndRPV"

# Load data set via quandl python api
data = quandl.get_table('WIKI/PRICES', paginate=True, date = { 'gte': '2018-01-01', 'lte': '2018-03-14' })

# options 
price_type_list = ['open','close','adj_open','adj_close']
colormap = all_palettes['Viridis'][len(options)]
colordict=dict()
for i, price_type in price_type_list:
	colordict[price_type] = colormap[i]
	

def datetime(x):
    return np.array(x, dtype=np.datetime64)

def create_figure(price_type_list):
	p=figure(x_axis_type='datetime', title='Quandl WIKI EOD Stock Prices')
	p.grid.grid_line_alpha=0.3
	p.xaxis.axis_label='Date'
	p.yaxis.axis_label='Stock Price'
	tickers=['GOOG']
	for ticker in tickers:
		df = data[data['ticker']==ticker]
		for price_type in price_type_list:
			p.line(x=datetime(df['date']), y=df[col], color=colordict[price_type], legend=ticker+': '+price_type)
	
	p.legend.location='top_left'
	
	return p


@app.route('/')
def index():
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
	

# @app.route('/about')
def about():
	return render_template('about.html')

if __name__ == '__main__':
	app.run(port=33507, debug=True)
