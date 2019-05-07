# -*- coding: utf-8 -*-
"""
Created on Tue Feb 26 10:35:44 2019

@author: ethan
"""
import os
import imageio
import re
from datetime import date
from time import time

import numpy as np
import pandas as pd
from colour import Color

from bokeh.io import export_png
from bokeh.plotting import figure
from bokeh.models import NumeralTickFormatter
from bokeh.models.tickers import FixedTicker

start_t = time()
path = r'C:\Users\ethan\projects\yieldcurve\version3\ '
path = path[:-1]

start = 4030
df = pd.read_csv('yielddata.csv').loc[start:,:].drop(columns='2')

df.index = range(df['1'].size)
df.iloc[:,1:] = df.iloc[:,1:]/100
def calcdate(x):
    x = x.split('/')
    return date(month = int(x[0]), day = int(x[1]), year = int(x[2]))

df['Date'] = df['Date'].apply(calcdate)
cm = np.linspace(0,.02,255)
colors = list(Color('red').range_to(Color('blue'), 256))
months = df.columns.to_series()[1:].astype(float)
ymax = df.iloc[:,-1].max()+.015
leg_txt = ['10 Year - 1 Month Spread: {:.2f}%',
           '10 Year - 3 Month Spread: {:.2f}%',
           '10 Year - 1 Year Spread: {:.2f}%',
           '10 Year - 2 Year Spread: {:.2f}%',
           '10 Year - 5 Year Spread: {:.2f}%']
spreads = df.apply(lambda x: x[9]- x[1:],axis=1)
yield_ind = [0,1,3,4,6]
spreads = spreads.iloc[:,yield_ind]

for i,row in df.iterrows():
    p = figure(width = 700, height = 700,
           title="Daily Yield Curve: {}".format(row['Date'].strftime('%B, %d, %Y')) ,
           x_axis_label = 'Duration (Months)',  x_axis_type ='log',
           y_axis_label = 'Interest Rate', 
           x_range = (1,360), y_range = (0,ymax))
    p.xgrid.grid_line_color = None
    p.ygrid.grid_line_color = None
    p.yaxis.formatter=NumeralTickFormatter(format="0.0%")
    p.xaxis.ticker = FixedTicker(ticks=months)
    
    p.line(months, row[1:],color='black')
    p.line([1,360],[row[9],row[9]], color = 'black',line_dash= 'dashed')
    
    for j in range(len(leg_txt)):
        spread = spreads.iloc[i,j]
        month = months[yield_ind[j]]
        p.line([month,month],[row[9],row[yield_ind[j]+1]],
               line_dash= 'dashed', line_width = 4,
               color = colors[np.searchsorted(cm,spread)].hex_l,
               legend = leg_txt[j].format(spread*100))
    
    if i >= 1:
        p.line(months, df.loc[i-1][1:],color='black', alpha = 2.0/3)
    if i >= 2:
        p.line(months,df.loc[i-2][1:],color='black', alpha = 1.0/3)
    p.legend.location = 'top_left'
    export_png(p,filename= path + str(row[0]) + '.png')
    print(df['1'].size -i, time() - start_t)

def sorted_aphanumeric(data):
    convert = lambda text: int(text) if text.isdigit() else text.lower()
    alphanum_key = lambda key: [ convert(c) for c in re.split('([0-9]+)', key) ] 
    return sorted(data, key=alphanum_key)

images = []
for file_name in sorted_aphanumeric(os.listdir(path)):
    if file_name.endswith('.png'):
        #print(file_name)
        file_path = os.path.join(path, file_name)
        images.append(imageio.imread(file_path))
imageio.mimsave(path + 'movie.gif', images)
print('Done u nerd', time() - start_t)