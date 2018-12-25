from bs4 import BeautifulSoup
import requests
import re
import pandas

# URL der data hentes fra
page = requests.get('https://www.ssb.no/kommunefakta/')
soup = BeautifulSoup(page.content, "html.parser")

# Funksjon som velger URL der data hentes fra
def velg_kommune(kommunenavn):
    url_base = 'https://www.ssb.no/kommunefakta/'
    url = url_base + kommunenavn
    return url
    

# Funksjon for å lage en liste med alle kommuner
def hent_kommuner():
    kommuner = []
    kommune_url = soup.find('', id="kommune-liste").contents
    for i in kommune_url:
        if i == '\n':
            pass
        else:
            kommuner.append(re.sub(r'^/kommunefakta/',"",i.a.get('href')))
    return kommuner

# Finne folketall
def finn_folketall():
    folketall = re.sub(r'\D',"",soup.find('', class_="tall").text)
    return [folketall]

# Finne utdanningsnivå
def finn_utdanningsnivaa():
    utdanning = soup.find('', id="highcharts-datatable-285358").descendants
    utdanning_navn = ["grunnskole", "videregaende", "universitet_kort", "universitet_lang","ingen_utdanning"]
    utdanning_tall = []
    for i in utdanning:
        if str(i).isdigit():
            utdanning_tall.append(i)
    utdanning = dict(zip(utdanning_navn,utdanning_tall))
    return utdanning_tall


# Finne religion/livssyn i prosentandel
def finn_religion():
    norske_kirke = list(soup.find('', id="kommunefaktatall-317475").descendants)
    norske_kirke = norske_kirke[8].span.previous_element
    annet_livssyn = list(soup.find('', id="kommunefaktatall-317473").descendants)
    annet_livssyn = annet_livssyn[8].span.previous_element
    return [norske_kirke, annet_livssyn]


# Forventet levealder for nyfødte
def finn_forventet_levealder():
    levealder_mann = soup.find('', id="kommunefaktatall-285276").span.previous_element
    levealder_kvinne = soup.find('', id="kommunefaktatall-285278").span.previous_element
    return [levealder_mann, levealder_kvinne]

# Driftsresultat i prosent
def finn_driftsresultat():
    driftsresultat = soup.find('', id="okonomi").p.next_element
    return [driftsresultat]     # Returnerer feil for tre kommuner. Fiks en eller annen gang.


# Finansielle nøkkeltall
def finn_finansielle_nokkeltall():
    laanegjeld_per_innbygger = soup.find('', id="kommunefaktatall-285209").span.previous_element
    driftsinntekter_per_innbygger = soup.find('', id="kommunefaktatall-285210").span.previous_element
    driftsutgifter_per_innbygger = soup.find('', id="kommunefaktatall-285214").span.previous_element
    return [laanegjeld_per_innbygger, driftsinntekter_per_innbygger, driftsutgifter_per_innbygger]


# Navn på alle kollonene til csv filen
tall_navn = ["Kommune", "Folketall", "Utdanning - Grunnskole", "Utdanning - Videregående", "Utdanning - Universitet (Kort)",
 "Utdanning - Universitet (Lang)", "Utdanning - Ingen", "Medlem i Den Norske Kirke", "Annet livssyn", "Forventet levealder (Mann)", 
 "Forventet levealder (Kvinne)", "Driftsresultat i prosent", "Lånegjeld per innbygger", "Driftsinntekter per innbygger", "Driftsutgifter per innbygger"]
# Har en liste med alle funksjonene som skal kjøres, slik at try/except kan enkelt brukes i en for-loop
funksjoner = [finn_folketall, finn_utdanningsnivaa, finn_religion, finn_forventet_levealder, finn_driftsresultat, finn_finansielle_nokkeltall]

kommuner = hent_kommuner() # Lager en liste av alle kommunene i Norge, hentet fra SSB.
rows_list = [] # Liste der hvert element er en rad i den ferdige csv-fiilen. En rad er alle tall for en kommune..

for kommune in kommuner: # Går gjennom listen av alle kommunene
    tall = [kommune] # Lagrer første element som navnet på kommunen
    url = velg_kommune(kommune) # Endrer url til den foreløpig valgte kommunen
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")
    for func in funksjoner: # For-loop som passer på at det lagres "N/A" dersom tallene ikke eksisterer for enkelte kommuner
        try:
            tall += func()
        except:
            tall += ["N/A"]
    rows_list.append(tall) # Appender navn på kommunen og alle dens tall
    print(tall)

dfKommune = pandas.DataFrame(data = rows_list, columns = tall_navn) # Lager en csv-fil med all info som har blitt samlet inn
#print(dfKommune)

dfKommune.to_csv('kommunedata_SSB.csv')

