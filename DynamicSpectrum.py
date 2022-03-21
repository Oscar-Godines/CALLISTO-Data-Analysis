""" El siguiente script solicita al usuario elegir un archivo de datos
en especifico, posteriormente realiza la curva de luz."""

# Los comentarios no tienen  acentos ,  para  evitar  problemas de  compilacion.

# Autor: Oscar B. Godines-Torres ------------- 25/01/2022. Contacto: oscargodinesosocar@gmail.com

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

files = askopenfilename()  # Se solicita al usuario elegir el archivo.

FIT = pyfits.open(files)                    #Abrir el archivo FIT.

hdr = FIT[0].header                         #Extraer datos de encabezado.
data = FIT[0].data                          #Extraer datos principales, tipo matriz.
time_c = FIT[1].data['time'][0]             #Extraer array de tiempo.
fre = FIT[1].data['frequency'][0]           #Extraer array de frecuencias.
time_i = FIT[0].header['TIME-OBS']          #Tiempo de inicio.
time_f = FIT[0].header['TIME-END']          #Tiempo final.
name = files[39:47]                         #Se extrae fecha de la direccion del archivo.

#Adaptar variable 'name' en caso de tener carpetas distintas, se extrae fecha 'aaaammdd'.

start = datetime.strptime( name+'_'+(time_i)+'000', '%Y%m%d_%H:%M:%S.%f')

#La variable flotante 'start' representa fecha y hora de inicio en formato 'aaaammdd_H:M:S'.

t = []                              #Declarar array t sin elementos.

delta = dt.timedelta(microseconds=(time_c[1]-time_c[0])*1000000)        #Delta de tiempo.

t.append(start+delta)                                               #Se agrega primer elemento al array t.

for j in range(len(time_c)):                                        #Se inicia un ciclo que rellena el array t.
    if j == len(time_c)-1:
        break
    else:
        delta = dt.timedelta(microseconds=(time_c[j+1]-time_c[j])*1000000)
        t.append(t[j]+delta)
        
        """El ciclo rellena el array t, de manera que agrega un delta por 
               cada elemento de time_c. Al final el array t debe tener un ultimo 
               elemento que coincida con time_f."""

fig = plt.figure(figsize=(8, 4))                                    #Se declara la figura.
ax = fig.add_subplot()                                              #Se agrega un eje en subfigura.

x_lim = mdates.date2num(t)                                          #Array que contiene el array fechas 't' convertido en flotantes.

data = data - data.mean(axis=1, keepdims=True) + 4                  #Se extrae media.
data = data.clip(-5, 120)                                           #Limitar valores pico.
data = data * 2500.0/255.0/25.4                                     #Conversion a dB.

plt.imshow(data,                                                    #Se grafican los datos.
           extent=[x_lim[0], x_lim[-1], fre[-1], fre[0]],
           aspect='auto',
           cmap='jet',                                              #afmhot,jet,CMRmap,gnuplot,rainbow,hot,magma,inferno,plasma,cubehelix
           vmin=-2,                                                 #Escala de intensidad.
           vmax=3)

ax.xaxis_date()
date_format = mdates.DateFormatter('%H:%M:%S')                      #Formato de eje tiempo.
ax.xaxis.set_major_formatter(date_format)                           #Establecer formato en el eje.

plt.xlabel('Time (UTC)')
plt.ylabel('Frequency (MHz)')

z = int(0)                                                          #6 variables int, las cuales representan las marcas en el eje.
x = int(len(x_lim)/6)                                               #Ahorran los problemas de extension de los datos.
c = int(2*(len(x_lim)/6))
v = int(3*(len(x_lim)/6))
b = int(4*(len(x_lim)/6))
n = int(5*(len(x_lim)/6))
m = int(len(x_lim)-1)

ax.set_xticks([x_lim[z], x_lim[x], x_lim[c],
                       x_lim[v], x_lim[b], x_lim[n], x_lim[m]])     #Establece marcas en los ejes.
plt.xticks(rotation=40)                                             #Rotacion de las marcas.

plt.subplots_adjust(bottom=.2)
plt.subplots_adjust(left=.2)

plt.title('MEXICO-LANCE-A Radio Flux Density ' + str(start)[0:10])

plt.grid(linewidth=0.3, linestyle='-', color='black')               #Rejila de fondo.

cbar = plt.colorbar()                                               #Barra de colores.
cbar.ax.set_ylabel('dB above background')

plt.show()                                                          #Se muestra el espectro dinamico. 
