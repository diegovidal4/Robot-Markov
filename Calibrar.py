#!/usr/bin/env python


from time import sleep
import nxt.bluesock
import nxt.locator
from nxt.sensor import *
from nxt.motor	import *
import numpy as np
import scipy as sp
	
#Inicializamos la conexion por bluetooth con el brick	
b=nxt.bluesock.BlueSock('00:16:53:0F:D2:F4').connect()

#Creamos los vectores con 0, y las variables de mu y sigma respectivas
blanco=np.zeros(100)
negro=np.zeros(100)

#Creamos la variable que setea el sensor de luz
sensor=Light(b, PORT_3)
sensor.set_illuminated(1)
#seteamos los valores del motor
m_izq=Motor(b,PORT_C)
m_der = Motor(b, PORT_C)


#Rescatamos los valores del sensor para el caso blanco, mientras giramos el robot en 90 grados
print "Colocar robot en superficie blanca, luego presione enter"
raw_input()
for i in range(0,99):
	x=sensor.get_sample()
	print 'Luz:', x
	blanco[i]=x
	m_izq.turn(100,90)
	sleep(2)

print "Cambie la superficie a negro, luego presione enter"
raw_input()

for i in range(0,99):
	x=sensor.get_sample()
	print 'Light:', x
	negro[i]=x
	m_izq.turn(100,90)
	sleep(2)


print 'Promedio blanco:',np.mean(blanco)
print 'Desviacion std blanca:',np.std(blanco)
print '**************************************'
print 'Promedio negro:',np.mean(negro)
print 'Desviacion std negro:',np.std(negro)



