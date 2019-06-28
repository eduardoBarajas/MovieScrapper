from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import subprocess
import os
import sys
import json
import requests
from datetime import date

def sendMoviesInParts(movs, year, api_url):
    movs_parts = []
    for n in range(len(movs)):
        if (n%50 == 0 and n > 0):
            movs_part = {}
            for m in range(((n//50)-1)* 50, n):
                movs_part[str(m)] = movs[str(m)]
            movs_parts.append(movs_part)
    movs_part = {}
    for n in range(len(movs_parts)*50, len(movs)):
        movs_part[str(n)] = movs[str(n)]
    movs_parts.append(movs_part)
    response = "" 
    for part in movs_parts:
        data = { 'movies': json.dumps(part), 'year': year, 'date': date.today().strftime("%d/%m/%Y"), 'count': len(part) }
        res = requests.post(url = api_url, data = data)
        response += "-["+res.text+"]-"
    return response 

def updateLinksFromMovie(online):
    with open('links_for_update.json', 'r') as file:
        #Se envia al servidor
        if (online == True):            
            api_url = "http://movies-server-movies-server.1d35.starter-us-east-1.openshiftapps.com/movies/update_links"
        else:        
            api_url = "http://localhost:8080/movies/update_links"
        links = json.loads(file.read())
        data = { 'links': json.dumps(links['movie_links']), 'year': links['year'], 'date': date.today().strftime("%d/%m/%Y"), 'name': links['name']}
        res = requests.put(url = api_url, data = data)
        print(res.text)

def addOrUpdateMovie(year, online):
    try:
        with open('ScrappedMoviesRexPelis/movies-{}.json'.format(year), 'r') as file:
            #Se envia al servidor
            api_url = ""
            if (online == True):            
                api_url = "http://movies-server-movies-server.1d35.starter-us-east-1.openshiftapps.com/movies/save"
            else:        
                api_url = "http://localhost:8080/movies/save"
            movs = json.loads(file.read())  
            if (len(movs) > 50):
                res = sendMoviesInParts(movs, year, api_url)        
            else:
                data = { 'movies': json.dumps(movs), 'year': year, 'date': date.today().strftime("%d/%m/%Y"), 'count': len(movs) }
                res = requests.post(url = api_url, data = data)
                res = res.text
            print(res)
    except:
        print("Ese anio no estaba almacenado en archivo")

def main(year, online, option):
    if (option == "ADD"):
        addOrUpdateMovie(year, online)
    elif (option == "UPDATE"):
        updateLinksFromMovie(online)
"""
Para ejecutar correctamente el script se debe ingresar el anio de la pelicula, si se quiere usar el servidor remoto debe utilizarse la palabra ONLINE de lo
contrario se debe escribir OFFLINE, ADD si se quiere agregar una pelicula y UPDATE si se quiere cambiar los links.

ej.
python localUploader.py 2000 ONLINE ADD
"""
if __name__ == "__main__":   
    year = int(sys.argv[1])
    online = str(sys.argv[2])
    if (online == "ONLINE"):
        online = True
    else:
        online = False
    option = str(sys.argv[3])
    main(year, online, option)

