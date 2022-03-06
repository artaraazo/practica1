#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar  4 17:05:46 2022

@author: artutaraperegmail.com
"""

from multiprocessing import Process
from multiprocessing import BoundedSemaphore, Semaphore
from multiprocessing import current_process
from multiprocessing import Array
from time import sleep
import random

NPROD = 3 #Número de productores.
NCONS = 1 #Número de consumidores.
N = 5 #Número de productos de cada productor.


def productor(sem_empty, sem_nonempty, storage, prid):
    v = 0 
    for i in range(N):
        print(f"productor {current_process().name} produciendo")
        sleep(random.random()/3)
        sem_empty[prid].acquire() #Es un "wait". Cuando el storage del productor que se está ejecutando se vacíe, comenzará a producir.
        v += random.randint(0,5) #Sumamos el número al anterior para generar el nuevo.
        storage[prid] = v #Almaceno el número.
        sem_nonempty[prid].release() #Es un "signal". Aviso de que el storage no está vacío.
        print(f"productor {current_process().name} almacenado {v}")
    sem_empty[prid].acquire() #Es un "wait". Dejo que el consumidor consuma el último producto.
    storage[prid] = -1 #Una vez producidos los "N" productos, colocamos en su casilla un -1.
    sem_nonempty[prid].release() #Es un "signal". Con objetivo de que el consumidor se ejecute, doy a señal de que he producido un falso último producto.
    
#Esta función me calcula el elemento mínimo de una lista y su posición, a excepción los -1, que cuando se encuentra uno no se trata, sino que se lo salta 
#y continúa analizando el resto de elementos de la lista.
def minimo(lista):
    i = 0
    while lista[i] == -1:
          i += 1
    minimo = lista[i]
    ind = i
    j = i+1
    while j < len(lista):
        if lista[j] < minimo and lista[j]!= -1:
            minimo = lista[j]
            ind = j
        j += 1
    return minimo, ind


def consumidor(sem_empty, sem_nonempty, storage):  
    salida = []
    for i in range(NPROD):
        sem_nonempty[i].acquire() #Es un "wait". Espera a que todos los productores hayan producido.
    listastop = [-1]*NPROD
    while listastop != list(storage): 
        print ("consumidor desalmacenando")
        sleep(random.random()/3)
        v, prid = minimo(list(storage)) #Escogemos el mínimo producto, que será el que vamos a desalmacenar.
        salida.append(v) #Lo añadimos a la lista final.
        sem_empty[prid].release() #Es un "signal". Vacío el storage del productor con el producto mínimo.
        print (f"consumidor consumiendo {v}")
        sem_nonempty[prid].acquire() #Es un "wait". Espero a que eñ productor lo llene.
    print("Lista final: ", salida )


def main():
    storage = Array('i',NPROD)
    sem_empty = []
    sem_nonempty = []
    for i in range(NPROD):
        non_empty = Semaphore(0)
        empty = BoundedSemaphore(1)
        sem_empty.append(empty)
        sem_nonempty.append(non_empty)
    producerlst = [Process(target = productor, 
                       name=f'prod_{i}', 
                       args=(sem_empty, sem_nonempty, storage,i))
                    for i in range (NPROD)]
    consumerlst = [Process(target = consumidor, args = (sem_empty, sem_nonempty, storage))]
    
    for p in producerlst + consumerlst:
        p.start()
         
    for p in producerlst + consumerlst:
        p.join()

if __name__ == "__main__":
   main()    
           
         
    
    


