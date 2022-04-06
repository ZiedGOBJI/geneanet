from bs4 import BeautifulSoup
import requests
import csv


url = "https://www.geneanet.org/fonds/individus/?go=1&nom=martin&prenom=fran%C3%A7ois&prenom_operateur=or&with_variantes_nom=&with_variantes_nom_conjoint=&with_variantes_prenom=&with_variantes_prenom_conjoint=&size=10"


def traitementURL(nom="",prenom="",):
    url = "https://www.geneanet.org/fonds/individus/?go=1&nom=" + nom + "&prenom=" + prenom + "&prenom_operateur=or&with_variantes_nom=&with_variantes_nom_conjoint=&with_variantes_prenom=&with_variantes_prenom_conjoint=&size=10" 
    return url 

def getNomPrenom():
    nom = input("Saisir nom")
    prenom = input("Saisir prénom")
    return nom, prenom





source = requests.get(url).text


soup = BeautifulSoup(source, 'lxml')

resOnly = soup.find("div", {"id":"table-resultats"})
# print(resOnly)

for a in resOnly.find_all('a'):
    print(a['href'])
    print(a["data-id-es"])
    # headline = a.text-large
    # print(headline)



res = soup.find("div", {"id":"content"})

for h1 in res.find_all('h1'):
    print(h1.with_tabs.name)
test = soup.find("div", class_="text-large")







'''
for article in soup.find_all('article'):
    headline = article.h2.a.text
    print(headline)

    summary = article.find('div', class_='entry-content').p.text
    print(summary)

    try:
        vid_src = article.find('iframe', class_='youtube-player')['src']

        vid_id = vid_src.split('/')[4]
        vid_id = vid_id.split('?')[0]

        yt_link = f'https://youtube.com/watch?v={vid_id}'
    except Exception as e:
        yt_link = None

    print(yt_link)

    print()


csv_file = open('fichier.csv', 'w')

csv_writer = csv.writer(csv_file)
csv_writer.writerow(['headline', 'summary', 'video_link'])

csv_writer.writerow([headline, summary, yt_link])


csv_file.close()
'''