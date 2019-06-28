#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Para que funcione correctamente el script y se puedan obtener las peliculas del sitio es necesario utilizar la libreria de
selenium y requests.

En resumen el script configura el driver de selenium para entrar a un sitio web y obtener informacion acerca de las peliculas que tienen almacenadas.
y despues con la libreria requests se mandan peticiones post para subirlas a un servidor.
"""
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import time
import subprocess
import os
import sys
import json
import requests
from datetime import date

"""

La funcion initWebDriver(), inicializa el driver(navegador) de google que se utilizara para navegar en los sitios.

"""
def initWebDriver():
    #necesita de un objeto Options() en el cual se agregan opciones de funcionamiento del driver.
    options = Options()
    #Headless y disable gpu se utilizan para ejecutar el script sin que aparezca el navegador en pantalla(background)
    #Si se quitan los dos argumentos el navegador aparecera y se podra ver que hace en cada paso.
    options.add_argument('--headless')
    options.add_argument('--disable-gpu') 
    #En el caso de quitar las opciones de arriba se regresa el webdriver.Chrome() sin parametros
    return webdriver.Chrome(chrome_options=options)

"""
La funcion main es la que se encarga de realizar toda la operacion de scrapping, para ello se le necesita dar los parametros, 
del anio en que comenzara a buscar y hasta donde, primeramente obtendra todos los links de ese anio y posteriormente entrara uno 
por uno hasta terminar la lista, una vez terminada todo se almacenara en un archivo json y posiblemente se suban al servidor.
"""
def main(start_year, end_year):
    #se obtiene el driver
    driver = initWebDriver()
    #Se obtendran los links de la pagina por cada anio
    for anio in range(int(start_year), int(end_year) + 1):
        print('Obteniendo peliculas del año {}'.format(anio)) 
        #Se inicializan los estructuras de datos que se utilizaran en la operacion
        movies_list = []
        movies_posters = []
        movies = dict()
        #Se ingresa al driver con la funcion get la pagina a la cual se ingresara primero.
        #En este caso las paginas son iguales cambiando solamente el anio que con la funcion format ingresa el anio en la parte del texto donde
        #esta el "  {}  "
        driver.get('https://www.rexpelis.com/peliculas-{}'.format(anio))
        #esta linea busca en el titulo de la pagina si contiene la palabra peliculas, creo que se puede quitar esta linea.
        assert "Peliculas" in driver.title
        #el driver tiene metodos para encontrar elementos de la pagina, en este caso la pagina tiene un boton con el cual al darle click
        #aparecen mas peliculas, por lo que se obtuvo para darle click.
        elem = driver.find_element_by_class_name("butmore")
        #Una vez obtenido el boton con un try ya que se va a intentar dar click hasta que el boton desaparezca.
        try:
            #while(True) es un ciclo infinito
            while(True):
                #cada vez que entre aqui el proceso se dormira 1.5 segundos(podria intentar bajarse para reducir el tiempo) y posteriormete se dara click en el boton
                time.sleep(1.5)
                elem.click()
        except:
            #cuando el boton de ver mas ya no exista en el documento de la pagina entrara aqui debido a la excepcion que causa
            #el driver tiene el siguiente emtodo que buscara todos los elementos con el nombre de la clase especificado
            #en este caso las peliculas comparten una clase llamada item-pelicula con lo cual se encuentran todas las que estan en pantalla.
            for el in driver.find_elements_by_class_name('item-pelicula'):
                #por cada elemento de pelicula se obtendra el link "href" y el poster "src" con las siguientes dos lineas
                movies_list.append(el.find_element_by_tag_name('a').get_attribute('href'))
                movies_posters.append(el.find_element_by_tag_name('img').get_attribute('src'))
        #se aumenta en uno el contador de peliculas.
        movie_count = 1
        #Por cada pelicula en la lista de peliculas (lista de links).
        for movie in movies_list:
            print("Pelicula #" + str(movie_count) + " de " + str(len(movies_list)))
            #se utilizara el driver para obtener la informacion de la pelicula.
            driver.get(movie)
            #cada pelicula tiene por arriba del reproductor unos tabs con los cuales al presionarlo se cambia el video, comparten la clase de tab-video
            video_tabs = driver.find_elements_by_class_name("tab-video")
            video_links = []
            #por cada tab encontrado, se dara click y se dormira el proceso(puede ser menos) para darle tiempo a que cambie el link y despues almacenarlo en la lista de video links.
            for tab in video_tabs:
                tab.click()
                time.sleep(2)
                video_links.append(driver.find_element_by_tag_name('iframe').get_attribute('src'))
            #La informacion de la pelicula la tiene en un contenedor con la clase info-content, cuando se quiere recuperar solo un elemento
            #se utiliza el find_element sin la "s", esto dara el primer elemento que tenga esa clase.
            datos_pelicula = driver.find_element_by_class_name('info-content')
            datos = []
            #debido a la forma en que esta escrito la informacion se obtuvo todo el texto del contenedor y despues se separo utilizando un ciclo.
            cadena_dato = ''
            for letra in datos_pelicula.text:
                #cada que la letra leida era un salto de linea  se almacenaba la linea en datos y se limpiaba la variable.
                if (letra == '\n'):
                    datos.append(cadena_dato)
                    cadena_dato = ''
                else:
                    #si no era salto de linea se agregaba a la cadena.
                    cadena_dato += letra
            #Una vez obtenida toda la informacion de la pelicula se almacenaba toda la info en un diccionario.
            #en este caso el diccionario se llama movies[] y dentro de los corchetes se mete la longitud de movies para que se fuera agregando
            #en su indice correspondiente 1, 2, 3, etc...
            movies[str(len(movies))] = {'href': movie, 'movieLinks': video_links, 'name': datos[0], 'poster': movies_posters[movies_list.index(movie)],
                'originalName': datos[1].split(':')[1], 'year': datos[2].split(':')[1], 'length': datos[3].split(':')[1].split("\\s+")[0],
                'genres': datos[4].split(':')[1], 'synopsis': datos[6], 'tags': datos[7], 'cast': datos[8].split(':')[1]}
            movie_count += 1
        #una vez almacenadas todas las peliculas en el diccionario se crea un archivo json con la siguiente linea.
        with open('ScrappedMoviesRexPelis/movies-{}.json'.format(anio), 'w+') as file:
            #la funcion write recibe como parametro una cadena de texto, en este caso se usa la libreria de json para 
            #crear la cadena en base al diccionario de movies que se creo, y el parametro indent=2 son los espacios que se dan en el texot, para ser mas legible.
            file.write(json.dumps(movies, indent=2))
            """
                En esta parte se envia al servidor pero falta modifcarse para que pueda enviar listas de mas de 50 peliculas a la vez.
            """
            #api_url = "http://movies-server-movies-server.1d35.starter-us-east-1.openshiftapps.com/movies/save"
            #api_url = "http://localhost:8080/movies/save"
            #data = { 'movies': json.dumps(movies, indent=2), 'year': anio, 'date': date.today().strftime("%d/%m/%Y"), 'count': len(movies) }
            #res = requests.post(url = api_url, data = data)
            #print(res.text)

if __name__ == "__main__":
    """
        Para ejecutar el script es necesario darle de parametros los anios, 

        por ejemplo:

        python rex_pelis_scrapper.py 2000 2001, buscara las peliculas desde el 2000 hasta el 2001.

        Si se quiere buscar solo de un anio se debe repetir, ej. python rex_pelis_scrapper.py 2000 2000
    """
    try:
        if (int(sys.argv[1]) < 1929):
            print('El anio minimo es 1929')
            exit()
        if (int(sys.argv[2]) < int(sys.argv[1]) or int(sys.argv[2]) > 2019):
            print('El segundo anio esta mal asegurate de ingresarlo bien')
            exit()
        if (len(sys.argv) < 3):
            main(sys.argv[1], sys.argv[1])
        else:
            main(sys.argv[1], sys.argv[2])
    except:
        print('debe tener los anios de inicio y final')
