from flask import Flask, render_template, request
import os

import scrapData as sd
import map

app = Flask(__name__)

def getSubfolder():
    return [os.path.basename(f.path) for f in os.scandir("./templates/map/") if f.is_dir()] 

def threadScrap(name, url):
    msg = "Récupération des données"
    if(url == ""):
        url = sd.traitementURL(name)
        print(url)
        url = sd.getArbreUrl(url)

    sd.scrapDataFromUrl(url)
    thrMap = Thread(target=threadMap,args=[name])
    thrMap.start()

    return render_template("index.html", name=name, subfolders=getSubfolder(), msgForm=msg)

def threadMap(name):
    msg = "Création de la carte"
    try:
        os.mkdir("./templates/map/" + name)
    except:
        pass

    map.mainMap(name)
    
    return render_template("index.html", name=name, subfolders=getSubfolder(), msgForm=msg)


@app.route('/')
def index():
    return render_template('index.html', subfolders=getSubfolder())

@app.route("/", methods = ['POST'])
def scrapData():
    name = request.form["nom"]
    url = request.form["url"]

    name = name.capitalize()

    print(name)
    print(url)
    
    if(name != ""):
        if(url == ""):
            url = sd.traitementURL(name)
            print(url)
            url = sd.getArbreUrl(url)

        sd.scrapDataFromUrl(url, name)

        try:
            os.mkdir("./templates/map/" + name)
        except:
            pass

        map.mainMap(name)

        return render_template("index.html", name=name, subfolders=getSubfolder())
    else:
        return render_template("index.html", name=name, subfolders=getSubfolder())


@app.route('/<name>')
def displayMap(name = ""):
    if(name in getSubfolder()):
        return render_template('index.html', name=name, subfolders=getSubfolder())
    return render_template('index.html', subfolders=getSubfolder())


@app.errorhandler(404)
def notfound(e):
    return "<h1>Page not found</h1>"


if __name__ == '__main__':
  app.run(debug=True)