from time import sleep
from flask import Flask, render_template, request
import subprocess as sp
import scrapData as sd
import map

import os
from os.path import isfile, join

from threading import Thread

app = Flask(__name__)

def getSubfolder():
    return [os.path.basename(f.path) for f in os.scandir("./templates/map/") if f.is_dir()] 

def threadScrap(nom, url):
    msg = "Récupération des données"
    if(url == ""):
        url = sd.traitementURL(nom)
        print(url)
        url = sd.getArbreUrl(url)

    thrMap = Thread(target=threadMap,args=[nom])
    thrMap.start()

    return render_template("index.html", name=nom, subfolders=getSubfolder(), msgForm=msg)

def threadMap(nom):
    msg = "Création de la carte"
    try:
        os.mkdir("./templates/map/" + nom)
    except:
        pass

    map.mainMap(nom)
    
    return render_template("index.html", name=nom, subfolders=getSubfolder(), msgForm=msg)

@app.route('/')
def index():
    return render_template('index.html', subfolders=getSubfolder())

@app.route("/", methods = ['POST'])
def scrapData():
    nom = request.form["nom"]
    url = request.form["url"]
    msg = ""

    print(nom)
    print(url)
    if(nom != ""):
        nom = nom.capitalize()
        msg = "Début récupération des données"
        
        thr = Thread(target=threadScrap, args=[nom, url])
        thr.start()
    else:
        msg = "Pas de nom renseigné"
    
    return render_template("index.html", name=nom, subfolders=getSubfolder(), msgForm=msg)

@app.route('/<name>')
def displayMap(name = ""):
  return render_template('index.html', name=name, subfolders=getSubfolder())


@app.errorhandler(404)
def notfound(e):
    return "<h1>Page not found</h1>"


if __name__ == '__main__':
  app.run(debug=True)