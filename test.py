from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import subprocess
import os
import sys
import json
import requests
from datetime import date

with open('movies-1970.json', 'r') as file:
    #Se envia al servidor
    #api_url = "http://movies-server-movies-server.1d35.starter-us-east-1.openshiftapps.com/movies/save"
    api_url = "http://localhost:8080/movies/save"
    movs = json.loads(file.read())
    data = { 'movies': json.dumps(movs), 'year': 1970, 'date': date.today().strftime("%d/%m/%Y"), 'count': len(movs) }
    res = requests.post(url = api_url, data = data)
    print(res.text)

"""
with open('links_for_update.json', 'r') as file:
    #Se envia al servidor
    #api_url = "http://movies-server-movies-server.1d35.starter-us-east-1.openshiftapps.com/movies/save"
    api_url = "http://localhost:8080/movies/update_links"
    links = json.loads(file.read())
    data = { 'links': json.dumps(links['movie_links']), 'year': links['year'], 'date': date.today().strftime("%d/%m/%Y"), 'name': links['name']}
    res = requests.put(url = api_url, data = data)
    print(res.text)
"""