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

annees =[]

# récupération des données
with open('dataSetPascal.json') as json_data:
    data = json.load(json_data) # type = list


# trouver année min et année max pour calibrer la barre
for dict in data:
  try:
    if(dict["ddn"] != ""):
      annees.append(dict["ddn"])
    if(dict["ddm"] != ""):
      annees.append(dict["ddm"])
  except:
    pass

print("année début : " + min(annees), "\nannée fin : " + max(annees))

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

geocoder = Nominatim(user_agent="http")

# on set les clés des dict (ce sont les années), on ne s'intéresse qu'à l'intervalle [année min, année max]
# set les valeurs des clés des lat et long
c = 0
for dict in data:
  print(dict)
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

  for k in range(int(min(annees)),int(max(annees))+1):
    data_pers["datetime"][c] = str(k)
    data_pers["etat"][c] = ""
    try:
      if(k >= int(dict["ddn"])):
        data_pers["lat"][c] = str(ville_naissance.latitude)
        data_pers["lon"][c] = str(ville_naissance.longitude)
        data_pers["etat"][c] = "Naissance"
        #print(dict["ldn"] + " : " + str(ville_naissance.latitude) + " " + str(ville_naissance.longitude))
    except:
      ""

    try:
      if(k >= int(dict["ddm"])):
        data_pers["lat"][c] = str(ville_mort.latitude)
        data_pers["lon"][c] = str(ville_mort.longitude)
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




'''
print(len(dict_datetime))
print(len(dict_lat_naissances))
print(len(dict_lon_naissances))
print(len(dict_lat_morts))
print(len(dict_lon_morts))

print(dict_datetime)
print(dict_lat_naissances)
print(dict_lon_naissances)
print(dict_lat_morts)
print(dict_lon_morts)
'''

df = pd.DataFrame(data_pers)

# print(df)
for d in data_pers:
  print(d)


# Naissances
fig = px.scatter_geo(df, 
                     lat='lat', 
                     lon='lon', 
                     scope='world',
                     projection="mercator", 
                     animation_frame="datetime",
                     animation_group="etat",
                     hover_name="etat",
                     hover_data={'lon':False,'lat':False,'etat':False, "datetime":False, "nom":True, "prenom":True, "ddn":True, "ddm":True, "ldn":True, "ldm":True, "url": True},
                     color="etat",
                     title='Affichage des morts et des naissances')

fig.update_layout(autosize=False, width=1000, height=1000)
fig.update(layout_coloraxis_showscale=False)


"""
# Morts
fig2 = px.scatter_geo(df, 
                     lat='lat_morts', 
                     lon='lon_morts', 
                     scope='world',
                     projection="mercator", 
                     animation_frame="datetime",
                     title='Affichage des morts',
                     )


fig2.update_layout(autosize=False, width=1000, height=1000)
fig2.update(layout_coloraxis_showscale=False)

fig.add_trace(fig2.data[-1])
"""
fig.write_html("./Confirmed.html")
fig.show()


def test():
    # geocoder = Nominatim(user_agent="http")

    df = px.data.gapminder()
    print(df)

    fig = px.scatter_geo(df, locations="iso_alpha", color="continent",
                        hover_name="country", size="pop",
                        animation_frame="year", projection="natural earth")

    fig.update_layout(autosize=False, width=1000, height=1000)
    fig.update(layout_coloraxis_showscale=False)

    # fig.write_html("./Confirmed.html")
    fig.show()