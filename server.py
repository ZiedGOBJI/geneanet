from flask import Flask, render_template, request
import subprocess as sp
import scrapData as sd

import os
from os.path import isfile, join


app = Flask(__name__)

def getSubfolder():
    return [os.path.basename(f.path) for f in os.scandir("./templates/map/") if f.is_dir()] 


@app.route('/')
def index():
    
    
    return render_template('index.html', subfolders=getSubfolder())

@app.route("/", methods=['POST'])
def scrapData():
    nom = request.form["nom"]
    url = request.form["url"]
    print(nom)
    print(url)
    if(url == ""):
        if(nom != ""):
            url = sd.traitementURL(nom)
    persUrl = sd.getArbreUrl(url)
    sd.scrapDataFromUrl(persUrl)

    return render_template("index.html", name=nom, subfolders=getSubfolder())

@app.route('/<name>')
def displayMap(name=""):
  print ('I got clicked!')

  return render_template('index.html', name = name, subfolders=getSubfolder())



if __name__ == '__main__':
  app.run(debug=True)