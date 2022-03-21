#Script para realizar automaticamente el analisis de los datos generados por el CALLISTO.
    
#Se recomienda usar un programador de tareas para ejecutar el codigo de manera periodica.
   
# Los comentarios no tienen acentos, para evitar problemas de compilacion.

# Autor: Oscar B. Godines-Torres --------- 09/02/2022.

# Nota: Cualquier modificacion favor de agregarla a la 'LISTA DE MODIFICACIONES' que se encuentra al final del código, no olvidar poner la fecha de la misma.
# Además, agregar la modificación al archivo 'Bitacora_CALLISTO_A.txt', para así mantener un orden.


import filecmp
from filecmp import dircmp
from importlib.resources import path
from pkgutil import extend_path
import astropy.io.fits as pyfits
import matplotlib.pyplot as plt
#from tkinter import Tk
#from tkinter import filedialog
#from tkinter.filedialog import askopenfilename
import datetime as dt
from datetime import datetime
import pylab
import time
import numpy as np
import os
import sys
from datetime import timedelta
import matplotlib.dates as mdates
import shutil


now = datetime.now()                                                   # Se obtiene la fecha y hora actual.

text = open('C:/Users/eagui/OneDrive/Escritorio/LOG_CALLISTO_A.txt','a')
text.write('\n\n\n Ejecutando ahora ---------> ' + str(now) + '\n')
text.write('Buscando archivos nuevos... \n\n')

print('Ejecutando ahora ---------> ' + str(now)) 
                                                                       # Se imprime la fecha y hora de ejecucion. 
print('Buscando archivos nuevos... \n')

dir1 = 'C:/CALLISTO-01/FITfiles'
dir2 = 'D:/Graficas_CALLISTO-A/FitFilesBackupA'                        # Directorios a comparar. 

comp = filecmp.dircmp(dir1,dir2,ignore=None,hide=None)   

new = comp.left_only                                                   #Variable tipo 'lista' que almacena los archivos que solo existen en FITfiles.

if len(new) == 0:
    print('No hay nuevos archivos. \n')                            #Caso 1: No hay nuevos archivos.
    text.write('No hay nuevos archivos. \n\n')
 


for i in range(len(new)):                                              #Se inicia un ciclo para tomar todos los nuevos archivos.
    text = open('C:/Users/eagui/OneDrive/Escritorio/LOG_CALLISTO_A.txt','a')
    news = str(new[i])                                                 #Convierte la variable lista a string.

    
    if news[24:28] == '0859':                                          #Caso 2: Es la hora de reinicio, el archivo se descarta. 
        print(new[i])
        files = 'C:/CALLISTO-01/FITfiles/' + news
        print(news[24:26] + ':' + news[26:28] + 
            ' UTC - Hora de reinicio, con menos de un segundo de registro. \n')
        shutil.copy(files, dir2)
        text.write(new[i] + '\n')
        text.write(news[24:26] + ':' + news[26:28] + 
            ' UTC - Hora de reinicio, con menos de un segundo de registro. \n\n')
        i = i + 1 
        
    else:                                                              #Caso 3: Hay archivos nuevos. 
        print(new[i])                                                  #Se imprime el archivo actual.

        text.write(new[i] + '\n\n')
        
        files = 'C:/CALLISTO-01/FITfiles/' + news 
              
        FIT = pyfits.open(files)                                       #Abrir el archivo FIT.
        
        hdr = FIT[0].header                                            #Extraer datos de encabezado.
        data = FIT[0].data                                             #Extraer datos principales, tipo matriz. 
        time_c = FIT[1].data['time'][0]                                #Extraer array de tiempo.
        fre = FIT[1].data['frequency'][0]                              #Extraer array de frecuencias.
        time_i = FIT[0].header['TIME-OBS']                             #Tiempo de inicio.
        time_f = FIT[0].header['TIME-END']                             #Tiempo final.
        name = files[39:47]                                            #Se extrae fecha de la direccion del archivo. 
        
         #Adaptar variable 'name' en caso de tener carpetas distintas, se extrae fecha 'aaaammdd'.

        start = datetime.strptime(name+'_'+(time_i)+'000', '%Y%m%d_%H:%M:%S.%f') 
        
         #La variable flotante 'start' representa fecha y hora de inicio en formato 'aaaammdd_H:M:S'.
        
        t = []                                                         #Declarar array t sin elementos.

        delta = dt.timedelta(microseconds=(time_c[1]-time_c[0])*1000000)    #Delta de tiempo.
                                                                       

        t.append(start+delta)                                          #Se agrega primer elemento al array t.

        for j in range(len(time_c)):                                   #Se inicia un ciclo que rellena el array t.
            if j == len(time_c)-1:
                break
            else:
                delta = dt.timedelta(microseconds=(time_c[j+1]-time_c[j])*1000000)
                t.append(t[j]+delta) 
                
            """El ciclo rellena el array t, de manera que agrega un delta por 
               cada elemento de time_c. Al final el array t debe tener un ultimo 
               elemento que coincida con time_f."""
            
        fig = plt.figure(figsize=(8, 4))                               #Se declara la figura.
        ax = fig.add_subplot()                                         #Se agrega un eje en subfigura.
        
        x_lim = mdates.date2num(t)                                     #Array que contiene el array fechas 't' convertido en flotantes.

        data = data - data.mean(axis=1, keepdims=True) + 4             #Se extrae media.
        data = data.clip(-5, 120)                                      #Limitar valores pico.              
        data = data * 2500.0/255.0/25.4                                #Conversion a dB.

        plt.imshow(
        data,                                                          #Se grafican los datos.
        extent=[x_lim[0], x_lim[-1], fre[-1],fre[0]], 
        aspect='auto',
        cmap='jet', #afmhot,jet,CMRmap,gnuplot,rainbow,hot,magma,inferno,plasma,cubehelix
        vmin=0,                                                        #Escala de intensidad.
        vmax=7) 

        ax.xaxis_date() 
        date_format = mdates.DateFormatter('%H:%M:%S')                 #Formato de eje tiempo.
        ax.xaxis.set_major_formatter(date_format)                      #Establecer formato en el eje.

        plt.xlabel('Time (UTC)')
        plt.ylabel('Frequency (MHz)')

        z = int(0)                                                     #6 variables int, las cuales representan las marcas en el eje.
        x = int(len(x_lim)/6)                                          #Ahorran los problemas de extension de los datos.
        c = int(2*(len(x_lim)/6))
        v = int(3*(len(x_lim)/6))
        b = int(4*(len(x_lim)/6))
        n = int(5*(len(x_lim)/6))
        m = int(len(x_lim)-1)       

        ax.set_xticks([x_lim[z], x_lim[x], x_lim[c],
              x_lim[v], x_lim[b], x_lim[n], x_lim[m]])                 #Establece marcas en los ejes.
        plt.xticks(rotation=40)                                        #Rotacion de las marcas
        
        plt.subplots_adjust(bottom=.2)
        plt.subplots_adjust(left=.2)

        plt.title('MEXICO-LANCE-A Radio Flux Density ' + str(start)[0:10])

        plt.grid(linewidth=0.3, linestyle='-', color='black')          #Rejila de fondo

        cbar = plt.colorbar()                                          #Barra de colores
        cbar.ax.set_ylabel('dB above background')

        #plt.show()

        namefile = news[0:33]                                          #Se extrae el nombre del archivo sin extension '.fit'

        fig.savefig('D:/Graficas_CALLISTO-A/EspectrosDinamicos_A/' + namefile)
        #Se guarda la figura en formato PNG.
        
        plt.close()                                                    #Cerrar figura. 

        data = FIT[0].data                                             #Se vuelven a leer los datos para regresar al formato.
        
        LC = []                                                        #Array curva de luz.

        sum = 0                                                        #Se declara la variable suma.

        for k in range(len(x_lim)):                                    #Ciclo que rellena el array LC.
            sum = 0
            for q in range(180):      
                sum = sum + data[q][k] 
        #Se suman los valores de potencia para todas las frecuencias de una columna.

            LC.append(sum)                                             #Se agrega una potencia total para cada elemento de tiempo.

        LC_norm = LC/max(LC)                                           #Normalizar (ValorMax = 1).
        
        fig = plt.figure(figsize=(8, 4))  
        ax = fig.add_subplot()

        x_lim = mdates.date2num(t) 
        
        plt.plot(t, LC_norm)                                          #Se grafican los datos 
        ax.xaxis_date()
        date_format = mdates.DateFormatter('%H:%M:%S')
        ax.xaxis.set_major_formatter(date_format)
        plt.xlabel('Time (UTC)')
        plt.ylabel('Normalized Amplitude')
        ax.set_xticks([x_lim[z], x_lim[x], x_lim[c],
                      x_lim[v], x_lim[b], x_lim[n], x_lim[m]])
        plt.xticks(rotation=40)
        ax.set_xlim(min(x_lim), max(x_lim))                           #Rango de tiempo.

        plt.subplots_adjust(bottom=.2)
        plt.subplots_adjust(left=.2)

        plt.title('MEXICO-LANCE-A Light Curve ' + str(start)[0:10])

        plt.grid(linewidth=0.3, linestyle='-', color='black')
        
        namefile = news[0:33] 

        fig.savefig('D:/Graficas_CALLISTO-A/CurvasDeLuz_A/' + namefile)

        plt.close('all')                                              #Se cierran todas las figuras.
        
        shutil.copy(files,dir2)                                       #El archivo analizado se copia al directorio 2.
        
        print('Listo. \n')                                            #Mensaje de iteracion completada.
        
        FIT.close()                                                   #Se recomienda cerrar el archivo FIT.

        text.write('Listo \n\n')
        text.close()

text = open('C:/Users/eagui/OneDrive/Escritorio/LOG_CALLISTO_A.txt','a')
text.write('Ejecución finalizada. \n\n')
text.close()

"""
------------------ LISTA DE MODIFICACIONES -------------------------------------------------------------------

          (ESCRIBE EN LAS SIGUIENTES LINEAS, NO USAR ACENTOS)
------------------------------------------------------------------------------------------------------------------

   Nombre             Fecha (aaaa/mm/dd)            Especifica el cambio
------------------------------------------------------------------------------------------------------------------

Oscar Godines             2022/02/11            - Se comento el comando 'plt.show()' para ahorrar recursos del
                                                  sistema, no es necesario observar las imagenes generadas.
------------------------------------------------------------------------------------------------------------------

Oscar Godines             2022/03/02            - Se retiró el #caso 1 del ciclo for principal, para imprimir
                                                  el aviso "no hay nuevos archivos".



"""






        
