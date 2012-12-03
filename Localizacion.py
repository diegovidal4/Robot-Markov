#!/usr/bin/env python

import sys
from time import sleep
import nxt.bluesock
import nxt.locator
from nxt.sensor import *
from nxt.motor	import *
import numpy as np
from scipy.stats import norm
import math
import random

class posicion:
	def __init__(self,a=0,b=0,c=0):
		self.x=a
		self.y=b
		self.bel=c

class Localizacion:


	#Constructor de la localizacion
	#arr: Lista de movimientos posibles hacia arriba
	#der: Lista de movimientos posibles hacia la derecha
	#aba: Lista de movimientos posibles hacia abajo
	#izq: Lista de movimientos posibles hacia la izquierda

	#arriba
#izquierda	#derecha      (Con el brick mirando hacia abajo)
	#abajo
	def __init__(self,x,y,s,b):
		self.arr=list()
		self.der=list()
		self.aba=list()	
		self.izq=list()
		self.posi=list()
		self.mov=list()
		self.Bel=0
		self.l=0
		self.umbral=0
		self.x=x
		self.y=y
		self.s=s
		self.b=b
		self.ca=0
		self.cab=0
		self.ci=0
		self.cd=0
		
	def bel(self,x,y):
		bel=np.zeros(x*y).reshape(x,y)
		bel=bel+(float(1)/float(x*y))
		self.Bel=bel

	def P(self,x,mu,sigma):
		p=norm(loc=mu,scale=sigma).pdf(x)
		return p

	def umbral(self,x,mub,sigmab):
		if x<(float(mub)-float(sigmab)): 
			return 0	#Estoy en negro
		else:
			return 1	#Estoy en blanco

	def normalizar(self,b):
		N=b.sum()
		for i in range(0,self.x):
			for j in range(0,self.y):
				b[i][j]=b[i][j]/N

	def prob(self,x):
		for i in range(0,self.x):
			for j in range(0,self.y):
				if L[i][j]==1:
					self.Bel[i][j]=self.Bel[i][j]*self.P(x,mun,sigman)
				else:
					self.Bel[i][j]=self.Bel[i][j]*self.P(x,mub,sigmab)
	def movizq(self,p):
		if (p.y)-1>=0 and self.s!="derecha":
			#print "izq:"
			#print p.x,p.y
			self.izq.append(p)
	def movder(self,p):
		if p.y+1<self.y and self.s!="izquierda":
			#print "der:"
			#print p.x,p.y
			self.der.append(p)
	def movarr(self,p):
		if p.x-1>=0 and self.s!="abajo":
			self.arr.append(p)
		
	def movaba(self,p):
		if p.x+1<self.x and self.s!="arriba":		
			self.aba.append(p)

	def obtener_max(self,d):
		m=max(d.items(), key=lambda x: x[1])
		for k,v in d.items():
			if v<m[1]:
				del d[k]
	

	def decision(self):
		ListaP={'arriba':0,'abajo':0,'derecha':0,'izquierda':0}
		for i in range(0,len(self.posi)-1):
			self.movizq(self.posi[i])
			self.movder(self.posi[i])
			self.movarr(self.posi[i])
			self.movaba(self.posi[i])

		for i in range(0,len(self.der)-1):
			ListaP['derecha']=ListaP['derecha']+(self.der[i].bel)/len(self.posi)
		for i in range(0,len(self.izq)-1):
			ListaP['izquierda']=ListaP['izquierda']+(self.izq[i].bel)/len(self.posi)
		for i in range(0,len(self.arr)-1):
			ListaP['arriba']=ListaP['arriba']+(self.arr[i].bel)/len(self.posi)
		for i in range(0,len(self.aba)-1):
			ListaP['abajo']=ListaP['abajo']+(self.aba[i].bel)/len(self.posi)

		self.obtener_max(ListaP)
		print ListaP.keys()
		dec=random.choice(ListaP.keys())
		print "Decision: ",dec			
		return dec
 	
	def contar_posibles(self):
		c=0
		for i in range(0,self.x):
			for j in range(0,self.y):
				if self.Bel[i][j]>=self.umbral:
					p=posicion(i,j,self.Bel[i][j])
					self.posi.append(p)
					c+=1
		return c
	
	
	def localizado(self):
		for i in range(0,self.x):
			for j in range(0,self.y):
				if self.Bel[i][j]>=0.9:
					return True,i,j
		return False,0,0

	def def_umbral(self,x):	
		self.umbral=0.001

	def mover(self,d):
		m_der=Motor(b,PORT_B)
		m_izq=Motor(b,PORT_C)
		m=SynchronizedMotors(m_der,m_izq,0)
		n=self.Bel
		if(d=="abajo"):
			n[self.cab,:]=0.00000001
			self.Bel=n
			self.cab=self.cab+1
			if(self.s=="abajo"):
				m.run(78)
				time.sleep(0.8)
				m.brake()
				self.s=d		
			elif(self.s=="arriba"):
				m_der.turn(80,720)
				time.sleep(2)
				m.run(78)
				time.sleep(0.8)
				m.brake()
				self.s=d			
			elif(self.s=="izquierda"):
				m_izq.turn(80,360)
				time.sleep(2)
				m.run(78)
				time.sleep(0.8)
				m.brake()
				self.s=d
			else:	
				m_izq.turn(80,360)
				time.sleep(2)
				m.run(78)
				time.sleep(0.8)
				m.brake()
				self.s=d	
				
			
		elif(d=="arriba"):
			aux=((self.x-1)-self.ca)
			n[aux,:]=0.00000001
			self.Bel=n
			self.ca=self.ca+1
			if(self.s=="abajo"):
				m_der.turn(80,720)
				time.sleep(2)
				m.run(78)
				time.sleep(0.8)
				m.brake()
				self.s=d		
			elif(self.s=="arriba"):
				m.run(78)
				time.sleep(0.8)
				m.brake()
				self.s=d			
			elif(self.s=="izquierda"):
				m_izq.turn(80,360)
				time.sleep(2)
				m.run(78)
				time.sleep(0.8)
				m.brake()
				self.s=d
			else:
				m_der.turn(80,360)
				time.sleep(2)
				m.run(78)
				time.sleep(0.8)
				m.brake()
				self.s=d
		elif(d=="izquierda"):
			aux=((self.y-1)-self.ci)
			n[:,aux]=0.00000001
			self.Bel=n
			self.ci=self.ci+1
			if(self.s=="abajo"):
				m_izq.turn(80,360)
				time.sleep(2)
				m.run(78)
				time.sleep(0.8)
				m.brake()
				self.s=d		
			elif(self.s=="arriba"):
				m_der.turn(80,360)
				time.sleep(2)
				m.run(78)
				time.sleep(0.8)
				m.brake()
				self.s=d			
			elif(self.s=="izquierda"):
				m.run(78)
				time.sleep(0.8)
				m.brake()
				self.s=d
			else:
				m_der.turn(80,720)
				time.sleep(2)
				m.run(78)
				time.sleep(0.8)
				m.brake()
				self.s=d
		else:
			
			n[:,self.cd]=0.00000001
			self.Bel=n
			self.cd=self.cd+1
			if(self.s=="abajo"):
				m_der.turn(80,360)
				time.sleep(2)
				m.run(78)
				time.sleep(0.8)
				m.brake()
				self.s=d		
			elif(self.s=="arriba"):
				m_izq.turn(80,360)
				time.sleep(2)
				m.run(78)
				time.sleep(0.8)
				m.brake()
				self.s=d		
			elif(self.s=="izquierda"):
				m_izq.turn(80,720)
				time.sleep(2)
				m.run(78)
				time.sleep(0.8)
				m.brake()
				self.s=d
			else:
				m.run(78)
				time.sleep(0.8)
				m.brake()
				self.s=d
			

#Inicializamos la conexion al bluetooth
np.set_printoptions(precision=7,suppress=True)
b=nxt.bluesock.BlueSock('00:16:53:0F:D2:F4').connect()

#Inicializamos los promedios y las desviaciones
mub=float(sys.argv[1])
sigmab=float(sys.argv[2])
mun=float(sys.argv[3])
sigman=float(sys.argv[4])
x=int(sys.argv[5])
y=int(sys.argv[6])
s=sys.argv[7]

#Seteamos el sensor de luz
sensor=Light(b, PORT_3)
sensor.set_illuminated(1)
sleep(3)


L=np.zeros(x*y).reshape(x,y)
#L[0][1]=1
#L[0][3]=1
#L[1][1]=1
#L[2][3]=1
#L[2][4]=1
#L[3][0]=1
#L[3][1]=1
#L[3][3]=1
#L[3][4]=1
#L[4][0]=1
#L[5][0]=1
#L[5][1]=1
#L[5][3]=1
#L[5][4]=1
#L[6][0]=1
#L[6][4]=1
L[0][0]=1
L[2][0]=1
L[2][2]=1
L[1][2]=1
loc=Localizacion(x,y,s,b)
loc.l=L
loc.bel(x,y)
for i in range(0,20):
		x=sensor.get_sample()
		print "luz: ",x	
		print "Bel:"
		print loc.Bel
		loc.prob(x)
		loc.def_umbral(i)
		print "Umbral:",loc.umbral
		print "Cantidad de cuadros sobre el umbral: ",loc.contar_posibles()
		d=loc.decision()
		loc.mover(d)
		print "Normalizada:"
		loc.normalizar(loc.Bel)
		print loc.Bel
		a,b,c=loc.localizado()
		if(a==True):
			print "Se ha localizado el robot",b,c
		else:
			print "Mover robot a cuadro siguiente"
			raw_input()








