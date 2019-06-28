from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import subprocess
import os
import sys
import json

def main(start_year, end_year):
    driver = webdriver.Chrome()
    for anio in range(int(start_year), int(end_year) + 1):
        print(anio)
        movies_list = []
        movies_posters = []
        movies = dict()
        driver.get('https://pelis28.tv/ver-pelicula/fecha-estreno/{}'.format(anio))
        if (str(anio) not in driver.title):
            continue
        else:
            print(driver.title)
            # Get scroll height
            last_height = driver.execute_script("return document.body.scrollHeight")
            while True:
                # Scroll down to bottom
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

                # Wait to load page
                time.sleep(3)

                # Calculate new scroll height and compare with last scroll height
                new_height = driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height
            for el in driver.find_elements_by_class_name('item'):
                movies_list.append(el.find_element_by_tag_name('a').get_attribute('href'))
                movies_posters.append(el.find_element_by_tag_name('img').get_attribute('src'))
            for movie in movies_list:
                driver.get(movie)
                video_tabs = driver.find_elements_by_class_name("tab-video")
                video_links = []
                for tab in video_tabs:
                    tab.click()
                    time.sleep(2)
                    video_links.append(driver.find_element_by_tag_name('iframe').get_attribute('src'))
                datos_pelicula = driver.find_element_by_class_name('info-content')
                datos = []
                cadena_dato = ''
                for letra in datos_pelicula.text:
                    if (letra == '\n'):
                        datos.append(cadena_dato)
                        cadena_dato = ''
                    else:
                        cadena_dato += letra
                movies[str(len(movies))] = {'href': movie, 'links_videos': video_links, 'nombre': datos[0], 'poster': movies_posters[movies_list.index(movie)],
                    'titulo_original': datos[1].split(':')[1], 'anio': datos[2].split(':')[1], 'duracion': datos[3].split(':')[1],
                    'generos': datos[4].split(':')[1], 'sinopsis': datos[6], 'tags': datos[7], 'reparto': datos[8].split(':')[1]}
            with open('movies-{}.json'.format(anio), 'w+') as file:
                file.write(json.dumps(movies, indent=2))
    driver.close()

if __name__ == "__main__":
    try:
        if (int(sys.argv[1]) < 1937):
            print('El anio minimo es 1937')
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