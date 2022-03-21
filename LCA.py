""" El siguiente script solicita al usuario elegir un archivo de datos
en especifico, posteriormente realiza la curva de luz."""

# Los comentarios no tienen  acentos ,  para  e vit ar  problemas de  compilacion.

# Autor: Oscar B. Godines-Torres ------------- 02/02/2022


from calendar import c
from importlib.resources import path
from pkgutil import extend_path
import astropy.io.fits as pyfits
import matplotlib.pyplot as plt 
from tkinter import Tk
from tkinter import filedialog
from tkinter.filedialog import askopenfilename
import datetime as dt
from datetime import datetime
import pylab
import time 
import numpy as np
import os, sys
from datetime import timedelta
import matplotlib.dates as mdates

files = askopenfilename()    #Se solicita al usuario elegir el archivo.

FIT = pyfits.open(files)

hdr = FIT[0].header
data = FIT[0].data
time_c = FIT[1].data['time'][0]
fre = FIT[1].data['frequency'][0]
time_i = FIT[0].header['TIME-OBS']
time_f = FIT[0].header['TIME-END']
name = files[39:47]

start = datetime.strptime( name+'_'+(time_i)+'000', '%Y%m%d_%H:%M:%S.%f')

t = []

delta = dt.timedelta(microseconds=(time_c[1]-time_c[0])*1000000)

t.append(start+delta)

for j in range(len(time_c)):
    if j == len(time_c)-1:
        break
    else:
        delta = dt.timedelta(microseconds=(time_c[j+1]-time_c[j])*1000000)
        t.append(t[j]+delta)

fig = plt.figure(figsize=(8, 4))
ax = fig.add_subplot()

x_lim = mdates.date2num(t)

LC = []

sum = 0

for k in range(len(x_lim)):
    sum = 0
    for q in range(180):
        sum = sum + data[q][k]

    LC.append(sum)

LC_norm = LC/max(LC)

z = int(0)
x = int(len(x_lim)/6)
c = int(2*(len(x_lim)/6))
v = int(3*(len(x_lim)/6))
b = int(4*(len(x_lim)/6))
n = int(5*(len(x_lim)/6))
m = int(len(x_lim)-1)


plt.plot(t, LC_norm)
ax.xaxis_date()
date_format = mdates.DateFormatter('%H:%M:%S')
ax.xaxis.set_major_formatter(date_format)
plt.xlabel('Time (UTC)')
plt.ylabel('Normalized Amplitude')
ax.set_xticks([x_lim[z], x_lim[x], x_lim[c],
                x_lim[v], x_lim[b], x_lim[n], x_lim[m]])
plt.xticks(rotation=40)
ax.set_xlim(min(x_lim), max(x_lim))

plt.subplots_adjust(bottom=.2)
plt.subplots_adjust(left=.2)

plt.title('MEXICO-LANCE-A Light Curve ' + str(start)[0:10])

plt.grid(linewidth=0.3, linestyle='-', color='black')

plt.show()