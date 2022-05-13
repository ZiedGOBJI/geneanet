# !pip install selenium
# !pip install bs4
# !pip install webdriver_manager
# !pip install requests


from bs4 import BeautifulSoup
import requests
import csv
import re
import time
from requests_html import HTMLSession # https://github.com/psf/requests-html
import json
import unicodedata
import random

'''
On cherche par rapport au nom de famille, les noms de famille de naissance sont utilisés. Il faut donc regarder le lieu de naissance des enfants pour savoir si la famille à bouger (suivie le/la partenaire).

Il faudrait arriver à trouver l'ancêtre le plus loin pour un nom de famille, puis analyser sa descendance :
Pour chaque enfant : 
    - Si c'est un garcon ou une fille on récupère les informations nescessaires + récupération des informations de l'épouse/époux
    - Si c'est un garcon on analysera la descendance


Informations à récupérer pour chaque personne :
 - Genre
 - Nom
 - Prénom
 - Date naissance
 - Lieu de naissance
 - Date mort
 - Lieu de mort


Visualisation (folium):
 - Sur une carte qui s'actualise tous les 10 ans, on affiche les naissances et les morts aux endroits correspondants

Avec le lieu de naissance de toute la famille, on peut voir comment ils se sont déplacé au fil des ans.

Améliorations :

Utilisation du lieu de mort, du lieu de certains événements, des informations des époux/épouses
'''


# Futur fonction à utiliser (pour saisie du nom prenom et création de l'url correspondante)
def traitementURL(nom):
    url = "https://www.geneanet.org/fonds/individus/?go=1&nom=" + nom + "&prenom=&prenom_operateur=or&with_variantes_nom=&with_variantes_nom_conjoint=&with_variantes_prenom=&with_variantes_prenom_conjoint=&size=10" 
    return url 


# Récupération du code html
def getSoup(url):
    request = requests.get(url)
    soup = BeautifulSoup(request.content, 'html.parser')
    return soup


def getArbreUrl(url):
    print("arbre url 1" + url)
    # Récupération du code html
    soup = getSoup(url)

    # Récupération de la div contenant toutes les urls en lien avec la recherche
    resOnly = soup.find("div", {"id":"table-resultats"})
    # print(resOnly)

    arbreUrl = ""
    # Récupération des urls
    for a in resOnly.find_all('a'):
        try:
            if (re.search("^arbres_utilisateur", a["data-id-es"])):  #^arbres_utilisateur
                arbreUrl = a["href"]
                break
        except:
            ""
    print("arbre url 2" + arbreUrl)
    return arbreUrl # Comporte l'url des pages utilisateurs si se sont des arbres utilisateurs


# Récupération des ascendants (remonter facilement à l'ancetre)
def getUrlDerAscendant(url):
    session = HTMLSession()
    r = session.get(url)
    soup = BeautifulSoup(r.html.html, 'html.parser')
    # Récupération du dernier ascendants
    # print(soup)
    urlDerAscendant = url

   
    try: 
        arbreGene =  soup.find("td", {"id":"ancestors"})
        trDerAscendant = arbreGene.findAll("tr")
        derAscendant = None
        cpt = 0

        while(derAscendant == None):
            tdDerAscendant = trDerAscendant[cpt*4].findAll("td")
            if(re.findall(r'colspan', str(tdDerAscendant[0])) == []):
                derAscendant = trDerAscendant[cpt*4].find("a")["href"]
            else:
                cpt += 1
        

        
        # Condition si le plus vieil ascendant est un ascendant direct de quelqu'un de celèbre
        if ("m=RL" in derAscendant):
            newDerAscendant = trDerAscendant[cpt*4].findAll("a")
            urlDerAscendant = "https://gw.geneanet.org/" + newDerAscendant[1]["href"]
        
        else:
            urlDerAscendant = "https://gw.geneanet.org/" + derAscendant

        urlDerAscendant = getUrlDerAscendant(urlDerAscendant)
        

    except:
        print("Pas d'autre ascendant")

    return urlDerAscendant

def getDataUrl(url):
    print(url)

    session = HTMLSession()
    r = session.get(url)
    soup = BeautifulSoup(r.html.html, 'html.parser')

    personne = {}

    personne["url"] = url
    
    # Récupération de l'html de l'ensemble des données d'une personne
    person_html = soup.find("div", {"id":"perso"})

    # Récupération des données concernant la personne (genre, nom, prenom)
    person_title = person_html.find("div", {"id":"person-title"})
    person_title = person_title.find("h1")

    try:
        personne["genre"] = person_title.find("img")["title"]
    except:
        personne["genre"] = None
    
    try:
        nomprenom = person_title.find_all("a")
        #nom_traite = unicodedata.normalize('NFD', nomprenom[0].text)
        personne["nom"] = unicodedata.normalize('NFD', nomprenom[1].text).encode('ascii', 'ignore').decode('utf-8')
        #prenom_traite = unicodedata.normalize('NFD', nomprenom[1].text)
        personne["prenom"] = unicodedata.normalize('NFD', nomprenom[0].text).encode('ascii', 'ignore').decode('utf-8')
    except:
        personne["nom"] = unicodedata.normalize('NFD', person_title.text).encode('ascii', 'ignore').decode('utf-8')
        personne["prenom"] = ""

    # Récupération des données concernant la personne (ddm, ldm, ddm, ldm)
    person_data_perso = person_html.find("ul")

    ldn = ""
    ldm = ""

    personne["ddn"] = ""
    personne["ddm"] = ""

    for li in person_data_perso.findAll("li"):
        li = li.text

        try:
            personne["ddn"] = re.findall("[0-9]{4}", re.findall("Né.*", li)[0])[0]
        except:
            ""
        try:
            personne["ddm"] = re.findall("[0-9]{4}", re.findall("Décédé.*", li)[0])[0]
        except:
            ""
        try:
            ldn = re.findall("à [- '\w+]*", re.findall("Né.*", li)[0])[0].replace("à ", "")
        except:
            ""
        try:
            ldn = re.findall("- [- '\w+]*", re.findall("Né.*", li)[0])[0].replace("- ", "").replace("à ","")
        except:
            ""
        try:
            ldm = re.findall("à [- '\w+]*", re.findall("Décédé.*", li)[0])[0].replace("à ", "")
        except:
            ""
        try:
            ldm = re.findall("- [- '\w+]*", re.findall("Décédé.*", li)[0])[0].replace("- ", "").replace("à ","")
        except:
            ""

    personne["ldn"] = unicodedata.normalize('NFD', ldn).encode('ascii', 'ignore').decode('utf-8')
    personne["ldm"] = unicodedata.normalize('NFD', ldm).encode('ascii', 'ignore').decode('utf-8')
    
    # date_naissance = person_data_perso.find("li").text
    # print(date_naissance)
    # print(re.search("Né le .* -", date_naissance))
    
    
    # Récupération des parents
    personne["pere"] = ""
    personne["mere"] = ""
    try:
        span_parent = person_html.find(text="Parents")
        h2_parent = span_parent.parent
        parents_data = h2_parent.findNext("ul")
        # parents_data = person_html.find("div", {"id":"parents"})
        # print(parents_data.find_all("a")[0]["href"])
        personne["pere"] = unicodedata.normalize('NFD', parents_data.findAll("a")[0].text).encode('ascii', 'ignore').decode('utf-8')
        personne["mere"] = unicodedata.normalize('NFD', parents_data.findAll("a")[1].text).encode('ascii', 'ignore').decode('utf-8')
    except:
        print("Erreur parents")

    # print(personne)
    return personne, person_html

    
def GetAllData(allperson, currenturl, getCurrentPers = True):

    personne, person_html = getDataUrl(currenturl)
    # print("soup" + str(person_html))
    if(getCurrentPers):
        allperson.append(personne)
        
    person_union = person_html.find("ul", {"class":"fiche_union"})

    try:
        person_epoux = person_union.findChildren("li" , recursive=False)

        for epoux_link in person_epoux:
            ul_child = epoux_link.find("ul")
            children = ul_child.findChildren("li", recursive=False)
            epoux, epoux_html = getDataUrl("https://gw.geneanet.org/" + epoux_link.find("a")["href"])
            allperson.append(epoux)
            
            try:
                for child_link in children:
                    url = "https://gw.geneanet.org/" + child_link.find("a")["href"]
                    child, child_html = getDataUrl(url)
                    allperson.append(child)
                    if(child["genre"] == "H"):
                        allperson = GetAllData(allperson, child["url"], getCurrentPers = False)
                        
            except:
                print("Err Children")
    except:
        print("Err Epoux")

    return allperson

def CompleteData(data):
    for pers in data:
        pere = {}
        
        if(pers["pere"] != ""):
            if(pers["ddn"] == "" or pers["ddm"] == "" or pers["ldn"] == "" or pers["ldm"] == ""):
                for pers2 in data:
                    if(pers["pere"] == pers2["nom"] + " " + pers2["prenom"]):
                        pere = pers2
            try:
                # Si pers n'a pas de ddn : on la set a ddn du pere + [20,40]
                if(pers["ddn"] == "" and pere["ddn"] != ""):
                    pers["ddn"] = str(int(pere["ddn"]) + random.randint(20,40))
                # Si pers n'a pas de ldn : on la set au ldn du pere
                if(pers["ldn"] == "" and pere["ldn"] != ""):
                    pers["ldn"] = pere["ldn"]
                # Si pers n'a pas de ldn : on la set au ldm du pere
                if(pers["ldn"] == "" and pere["ldm"] != ""):
                    pers["ldn"] = pere["ldm"]
            except:
                pass
            # Si pers n'a pas de ddm : on la set a la ddn + [65,85]
            if(pers["ddm"] == "" and pers["ddn"] != ""):
                pers["ddm"] = str(int(pers["ddn"]) + random.randint(65,85))
                #Si la date de mort prévue est après 2022, on ne l'initialise pas (on ne prédit pas le futur)
                if (int(pers["ddm"]) > 2022):
                    pers["ddm"] = ""
            # Si pers n'a pas de ddn mais ddm : on la set a la ddm - [65,85]
            if(pers["ddn"] == "" and pers["ddm"] != ""):
                pers["ddn"] = str(int(pers["ddm"]) - random.randint(65,85))
            # Si pers n'a pas de ldm : on la set au ldn
            if(pers["ldm"] == "" and pers["ldn"] != ""):
                pers["ldm"] = pers["ldn"]
            # Si pers n'a pas de ldn : on la set au ldm
            if(pers["ldn"] == "" and pers["ldm"] != ""):
                pers["ldn"] = pers["ldm"]

    return data




# -------------------------- Lancement du scraping -------------------------- #

def scrapDataFromUrl(url, nom):
    urlDerAscendant = ""
    print("url de base : " + url)
    data = []
    
    urlDerAscendant = getUrlDerAscendant(url)
    print("Url dernier ascendant : " + urlDerAscendant)
    
    data = GetAllData(data, urlDerAscendant)

    data = CompleteData(data)

    with open('dataSet' + nom + '.json', 'w+') as outfile:
        json.dump(data, outfile)







# ----------------------------------- Test ----------------------------------- #


def testLdn():
    test = """Né vers 1619 - à Souvert (commune de Chissey en Morvan ou Lucenay l'Evèque)"""

    try:
        res = re.findall("à [ '\w+]*", test)[0].replace("à ", "")
    except:
        ""

    try:
        res = re.findall("- [ '\w+]*", test)[0].replace("- ", "").replace("à ","")
    except:
        ""
    print(res)

# testLdn()