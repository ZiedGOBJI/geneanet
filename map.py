# !pip install plotly
# !pip install nominatim
# !pip install geopy

import numpy as np
import pandas as pd
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from geopy.geocoders import Nominatim
import csv
import json
import random





def getJsonData(dataName):
  # récupération des données
  with open('dataSet' + dataName + '.json') as json_data:
      data = json.load(json_data) # type = list
  return data


def findYearMinMax(data):
  # trouver année min et année max pour calibrer la barre
  annees = []
  for dict in data:
    try:
      if(dict["ddn"] != ""):
        annees.append(dict["ddn"])
      if(dict["ddm"] != ""):
        annees.append(dict["ddm"])
    except:
      pass
  print("année début : " + min(annees), "\nannée fin : " + max(annees))

  return annees


def initializeDataPers():
  # dictionnaires
  data_pers = {}
  data_pers["datetime"] = {}
  data_pers["etat"] = {}
  data_pers["lat"] = {}
  data_pers["lon"] = {}
  data_pers["nom"] = {}
  data_pers["prenom"] = {}
  data_pers["url"] = {}
  data_pers["ldn"] = {}
  data_pers["ldm"] = {}
  data_pers["ddn"] = {}
  data_pers["ddm"] = {}
  return data_pers

def getGeocoder():
    return Nominatim(user_agent="http")

def setDataFrameMap(data, annees):
  geocoder = getGeocoder()
  data_pers = initializeDataPers()
  # on set les clés des dict (ce sont les années), on ne s'intéresse qu'à l'intervalle [année min, année max]
  # set les valeurs des clés des lat et long
  c = 0
  lendata = len(data)
  for dict in data:
    print(str(round(((data.index(dict)*100)/lendata),2)) + "%")
    ville_naissance = ""
    ville_mort = ""
    try:
      if(dict["ldn"] != ""):
        ville_naissance = geocoder.geocode(dict["ldn"])
    except:
      pass
    try:
      if(dict["ldm"] != ""):
        ville_mort = geocoder.geocode(dict["ldm"])
    except:
      pass

    # introduction d'un bruitx et d'un bruity afin d'empêcher la superposition des individus
    bruitx = random.uniform(-0.006,0.006)
    bruity = random.uniform(-0.006,0.006)
    for k in range(int(min(annees)),int(max(annees))+1):
      data_pers["datetime"][c] = str(k)
      data_pers["etat"][c] = ""

      try:
        if(k >= int(dict["ddn"])):
          data_pers["lat"][c] = str(ville_naissance.latitude + bruitx)
          data_pers["lon"][c] = str(ville_naissance.longitude + bruity)
          data_pers["etat"][c] = "Naissance"
          #print(dict["ldn"] + " : " + str(ville_naissance.latitude) + " " + str(ville_naissance.longitude))
      except:
        ""

      try:
        if(k >= int(dict["ddm"])):
          data_pers["lat"][c] = str(ville_mort.latitude + bruitx)
          data_pers["lon"][c] = str(ville_mort.longitude + bruity)
          data_pers["etat"][c] = "Mort"
          #print(dict["ldm"] + " : " + str(ville_mort.latitude) + " " + str(ville_mort.longitude))
      except:
        ""

      data_pers["nom"][c] = dict["nom"]
      data_pers["prenom"][c] = dict["prenom"]
      data_pers["url"][c] = dict["url"]
      data_pers["ldn"][c] = dict["ldn"]
      data_pers["ldm"][c] = dict["ldm"]
      data_pers["ddn"][c] = dict["ddn"]
      data_pers["ddm"][c] = dict["ddm"]

      c+=1

  return pd.DataFrame(data_pers)

def setDataFrameMapPop(data, annees):
  geocoder = getGeocoder()
  
  data_pers = {}
  data_pers["datetime"] = {}
  data_pers["size"] = {}
  data_pers["lat"] = {}
  data_pers["lon"] = {}
  data_pers["lieu"] = {}
  

  # on set les clés des dict (ce sont les années), on ne s'intéresse qu'à l'intervalle [année min, année max]
  # set les valeurs des clés des lat et long
  c = 0
  lendata = len(data)
  allcity = {}
  for dict in data:
    
    try:
      if(dict["ldn"] != ""):
        ville = geocoder.geocode(dict["ldn"])
        print(allcity.keys())
        print(ville.latitude)
        print(str(ville.latitude) + " " + str(ville.longitude) not in list(allcity.keys()))
        if(str(ville.latitude) + " " + str(ville.longitude) not in list(allcity.keys())):
          allcity[str(ville.latitude) + " " + str(ville.longitude)] = []
        allcity[str(ville.latitude) + " " + str(ville.longitude)].append(int(dict["ddn"]))
    except:
      pass
  
  print(allcity)

  for city in allcity:
    
    for k in range(int(min(annees)),int(max(annees))+1):
      first = True
      if(k in allcity[city]):
        data_pers["datetime"][c] = str(k)
        data_pers["size"][c] = 0
        try:
          if(k >= int(dict["ddn"])):
            data_pers["lat"][c] = str(ville.latitude)
            data_pers["lon"][c] = str(ville.longitude)
            if(first):
              data_pers["lieu"][c] = dict["ldn"]
              data_pers["size"][c] = 0
              first = False
            else:
              data_pers["size"][c] = data_pers["size"][c-1] + 1
            #print(dict["ldn"] + " : " + str(ville_naissance.latitude) + " " + str(ville_naissance.longitude))
        except:
          pass
        c+=1

  return pd.DataFrame(data_pers)


def createMapPop(df, name):

  # Évenements (naissances et morts)
  fig = px.scatter_geo(df, 
                      lat='lat', 
                      lon='lon', 
                      scope='world',
                      projection="mercator", 
                      animation_frame="datetime",
                      hover_name="lieu",
                      hover_data={'lon':False, 'lat':False, "datetime":False, "lieu":True, "size":True},
                      size="size",
                      title='Déplacement de la famille : ' + name)

  fig.update_layout(autosize=False, width=1000, height=500, geo=dict(
            projection_scale=10, #this is kind of like zoom
            center=dict(lat=48.683569, lon=7.858726)))
  fig.update(layout_coloraxis_showscale=False)
  return fig

def createMap(df, name):

  # Évenements (naissances et morts)
  fig = px.scatter_geo(df, 
                      lat='lat', 
                      lon='lon', 
                      scope='world',
                      projection="mercator", 
                      animation_frame="datetime",
                      animation_group="etat",
                      hover_name="etat",
                      hover_data={'lon':False, 'lat':False, 'etat':False, "datetime":False, "nom":True, "prenom":True, "ddn":True, "ddm":True, "ldn":True, "ldm":True, "url": True},
                      color="etat",
                      title='Déplacement de la famille : ' + name)

  fig.update_layout(autosize=False, width=1000, height=550, geo=dict(
            projection_scale=10, #this is kind of like zoom
            center=dict(lat=48.683569, lon=7.858726)))
  fig.update(layout_coloraxis_showscale=False)


  fig2 = px.scatter_geo(df, 
                      lat='lat', 
                      lon='lon', 
                      scope='world',
                      projection="mercator", 
                      animation_frame="datetime",
                      animation_group="etat",
                      hover_name="etat",
                      hover_data={'lon':False, 'lat':False,"etat":False, "datetime":False, "nom":True, "prenom":True, "ddn":True, "ddm":True, "ldn":True, "ldm":True, "url": True},
                      color="etat",
                      title='Déplacement de la famille : ' + name)

  fig.add_trace(fig2.data[0])
  return fig

def saveMap(fig, dataName):
  fig.write_html("./templates/map/" + dataName + "/Map" + dataName + ".html")

def saveMapPop(fig, dataName):
  fig.write_html("./templates/map/" + dataName + "/MapPop" + dataName + ".html")
  
def mainMap(dataName):
  data = getJsonData(dataName)
  annees = findYearMinMax(data)
  
  df = setDataFrameMap(data, annees)
  
  fig = createMap(df, dataName)
  saveMap(fig, dataName)

def testPop():
  name = "Martin"
  data = getJsonData(name)
  annees = findYearMinMax(data)

  df = setDataFrameMapPop(data, annees)
    
  fig = createMapPop(df, name)
  saveMapPop(fig, name)

def test():
    # geocoder = Nominatim(user_agent="http")

    df = px.data.gapminder()
    print(df)

    fig = px.scatter_geo(df, locations="iso_alpha", color="continent",
                        hover_name="country", size="pop",
                        animation_frame="year", projection="natural earth")

    fig.update_layout(autosize=False, width=1000, height=500)
    fig.update(layout_coloraxis_showscale=False)

    fig.write_html("./test.html")
    fig.show()

# mainMap("Kevin")