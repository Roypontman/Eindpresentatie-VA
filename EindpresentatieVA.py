#!/usr/bin/env python
# coding: utf-8

# # Casus Eindopdracht Visual Analytics- Giel, Roy 

# ## Minor Data Science
# ### Studenten: Giel Suweijn (500835117) en Roy Pontman (500826482)

# ## Inladen Packages

# In[2]:
from PIL import Image
import pandas as pd
import geopandas as gpd
import numpy as np
import requests
import plotly.express as px
import plotly.figure_factory as ff
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from shapely.geometry import Point
import missingno as msno
from statsmodels.formula.api import ols
#!pip install streamlit
import streamlit as st
from fuzzywuzzy import fuzz
import datetime
from datetime import date
import seaborn as sns
import matplotlib.pyplot as plt
import streamlit_folium as st_folium
from streamlit_folium import folium_static
import folium
# ## Ophalen Dataset Bodemgebruik door middel van API
r1 = requests.get('https://opendata.cbs.nl/ODataApi/odata/37105/TypedDataSet')
x1 = r1.json()
df1 = pd.DataFrame(x1['value'])
r2 = requests.get('https://opendata.cbs.nl/ODataApi/odata/37105/RegioS')
x2 = r2.json()
df2 = pd.DataFrame(x2['value'])
r3 = requests.get('https://opendata.cbs.nl/ODataApi/odata/37105/Perioden')
x3 = r3.json()
df3 = pd.DataFrame(x3['value'])
# ## Tot een dataset/frame komen, mergen van de drie bovenstaande dataframes
df3 = df3.rename(columns={"Key": "Perioden"})
dfstap1 = df2.rename(columns={"Key": "RegioS"})
df2nieuw = dfstap1.drop(columns = ['Description', 'CategoryGroupID'])
data_stap1 = df1.merge(df3, on='Perioden')
data_stap2 = data_stap1.merge(df2nieuw, on='RegioS')
# ## Hernoemen/droppen van kolommen,waarden
data_stap3 = data_stap2.replace({'Groningen (PV)': 'Groningen',
                         'Noord-Holland (PV)': 'Noord-Holland',
                         'Zuid-Holland (PV)': 'Zuid-Holland',
                         'Friesland (PV)': 'Friesland',
                         'Zeeland (PV)': 'Zeeland',
                         'Gelderland (PV)': 'Gelderland',
                         'Overijssel (PV)': 'Overijssel',
                         'Utrecht (PV)': 'Utrecht',
                         'Limburg (PV)': 'Limburg',
                         'Drenthe (PV)': 'Drenthe',
                        'Flevoland (PV)': 'Flevoland',
                         'Noord-Brabant (PV)': 'Noord-Brabant'})

data_stap4 = data_stap3.rename(columns={"Title_x": "Jaar", "Title_y" : "Locatie"})
data_stap4 = data_stap4.drop(columns=['Status', 'RegioS', 'Perioden', 'Description', 'Buitenwater_26'])
data_stap5= data_stap4.dropna()
# ## Geojson inladen van alle provincies in Nederland
provincies_geo = gpd.read_file('Provincies.geojson')
# ## Deze geojson bewerken/manipuleren
geo_data = provincies_geo.rename(columns=({'OMSCHRIJVI':'Locatie'}))
geo_data1 = geo_data.replace(regex={r'Fryslân': 'Friesland'})
data_stap6 = geo_data1.merge(data_stap5, on= 'Locatie')

data_stap7 = data_stap6.rename(columns ={'TotaalVerkeersterrein_2' : 'Infra1',
                                        'Spoorterrein_3' : 'Infra2',
                                        'Wegverkeersterrein_4' : 'Infra3',
                                        'Vliegveld_5' : 'Infra4',
                                         
                                        'TotaalBebouwdTerrein_6' : 'Bebouwd1',
                                        'Woonterrein_7' : 'Bebouwd2',
                                        'Bedrijventerreinen_8' : 'Bebouwd3',
                                        'SociaalCultureleVoorzieningen_9' : 'Bebouwd4',
                                        'TotaalSemiBebouwdTerrein_10' : 'Bebouwd5',
                                        'Delfstofwinplaats_11' : 'Bebouwd6',
                                        'Bouwterrein_12' : 'Bebouwd7',
                                        'OverigeSemiBebouwdeTerreinen_13' : 'Bebouwd8',
                                         
                                         
                                        'Sportterrein_16' : 'Onverhard1',
                                        'TotaalRecreatieterrein_14' : 'Onverhard2',
                                         'OverigeRecreatieterreinen_17' : 'Onverhard3',
                                         
                                         'TotaalAgrarischTerrein_18' : 'Landbouw1',
                                         'TerreinVoorGlastuinbouw_19' : 'Landbouw2',
                                         'OverigAgrarischTerrein_20' : 'Landbouw3',
                                         
                                         
                                         
                                        'TotaalBosEnOpenNatuurlijkTerrein_21' : 'Natuur1',
                                        'Bos_22' : 'Natuur2',
                                        'OpenNatuurlijkeTerreinen_23' : 'Natuur3',
                                         'ParkEnPlantsoen_15': 'Natuur4',
                                         
                                         'Binnenwater_25' : 'Water',
                                         
                                         'Totaal_1' : 'Totaal'
                                        })
# ## Kolommen samenvoegen en overige weglaten
data_stap7['Natuur'] = data_stap7["Natuur1"] +  data_stap7["Natuur2"] +  data_stap7["Natuur3"] +  data_stap7["Natuur4"]
data_stap7['Infra'] = data_stap7["Infra1"] +  data_stap7["Infra2"] +  data_stap7["Infra3"] +  data_stap7["Infra4"]
data_stap7['Bebouwd'] = data_stap7["Bebouwd1"] +  data_stap7["Bebouwd2"] +  data_stap7["Bebouwd3"] +  data_stap7["Bebouwd4"]+  data_stap7["Bebouwd5"]+  data_stap7["Bebouwd4"]+  data_stap7["Bebouwd6"]+  data_stap7["Bebouwd7"]+  data_stap7["Bebouwd8"]
data_stap7['Onverhard'] = data_stap7["Onverhard1"] +  data_stap7["Onverhard2"] +  data_stap7["Onverhard3"] 
data_stap7['Landbouw'] = data_stap7["Landbouw1"] +  data_stap7["Landbouw2"] +  data_stap7["Landbouw3"]

data_stap8 = data_stap7.drop(columns = [ 'Natuur1', 'Natuur2', 'Natuur3', 'Natuur4',
                               'Infra1', 'Infra2', 'Infra3', 'Infra4',
                               'Bebouwd1', 'Bebouwd2', 'Bebouwd3', 'Bebouwd4','Bebouwd5', 'Bebouwd6', 'Bebouwd7', 'Bebouwd8',
                               'Onverhard1', 'Onverhard2', 'Onverhard3', 
                               'Landbouw1', 'Landbouw2', 'Landbouw3'
                               ])
# ## Centroïden plaatsen voor de popups in de map
data_stap8['centroid'] = data_stap8.centroid
data_stap8['centroid'] = data_stap8['centroid'].to_crs(epsg=4326)
# ## Datastap 8 omschrijven naar een betere naam
bodemgebruik = data_stap8[['ID','Jaar','Locatie','Water','Natuur','Infra','Bebouwd','Onverhard','Landbouw','geometry','centroid']]
bodemgebruik['Jaar'] = pd.to_datetime(bodemgebruik['Jaar']).dt.year
bodemgebruik = bodemgebruik[bodemgebruik.Jaar > 2000]


# ## Ophalen Dataset Watergebruik door middel van API
url = "https://opendata.cbs.nl/ODataApi/odata/82883NED/TypedDataSet"
response = requests.get(url)
json = response.json()
data = pd.DataFrame(json)
df = data['value']
lijst = []
for x in df:
    inhoud = [x['ID'],x['Watergebruikers'], x['Perioden'], x['TotaalLeidingwater_1'],
              x['Drinkwater_2'],x['Industriewater_3'],x['TotaalGrondwater_4'],
              x['GebruikVoorKoeling_5'],x['OverigGebruikGrondwater_6'],
              x['TotaalOppervlaktewater_7'],x['ZoetOppervlaktewater_8'],x['ZoutOppervlaktewater_9']]
    lijst.append(inhoud)
    
df_watergebruik = pd.DataFrame(lijst, columns = ['ID','Watergebruikers','Perioden',
                                                 'TotaalLeidingwater_1','Drinkwater_2','Industriewater_3',
                                                 'TotaalGrondwater_4','GebruikVoorKoeling_5','OverigGebruikGrondwater_6',
                                                 'TotaalOppervlaktewater_7','ZoetOppervlaktewater_8','ZoutOppervlaktewater_9'])
df_watergebruik.head()
df_watergebruik.Watergebruikers.unique()
Watergebruikers = ['301000 ','1050010','305700 ','307500 ','346600 ','348000 ','350000 ','354200 ','383100 ','389100 ']
df_watergebruik = df_watergebruik.loc[df_watergebruik['Watergebruikers'].isin(Watergebruikers)]
df_watergebruik.reset_index(inplace = True, drop = True)
df_watergebruik.isna().sum()
df_watergebruik = df_watergebruik.fillna(0)
df_watergebruik['Jaar'] = df_watergebruik['Perioden'].str[:4]
df_watergebruik.drop(['Perioden','ID'],axis=1, inplace=True)
df_watergebruik['Watergebruikers'] = df_watergebruik['Watergebruikers'].astype(str)
# Alle sectoren zijn gecodeerd in de download van de CSV, hierdoor moeten ze allemaal weer de goede naam krijgen.
for i,column in df_watergebruik.iterrows():
    if column['Watergebruikers'] == '301000 ':
        df_watergebruik.loc[i, 'Watergebruikers'] = 'Landbouw'
    if column['Watergebruikers'] == '1050010':
        df_watergebruik.loc[i, 'Watergebruikers'] = 'Huishoudens'
    if column['Watergebruikers'] == '305700 ':
        df_watergebruik.loc[i, 'Watergebruikers'] = 'Delfstofwinning'
    if column['Watergebruikers'] == '307500 ':
        df_watergebruik.loc[i, 'Watergebruikers'] = 'Industrie'
    if column['Watergebruikers'] == '346600 ':
        df_watergebruik.loc[i, 'Watergebruikers'] = 'Energievoorziening'
    if column['Watergebruikers'] == '348000 ':
        df_watergebruik.loc[i, 'Watergebruikers'] = 'Water- en afvalbedrijven'
    if column['Watergebruikers'] == '350000 ':
        df_watergebruik.loc[i, 'Watergebruikers'] = 'Bouw'
    if column['Watergebruikers'] == '354200 ':
        df_watergebruik.loc[i, 'Watergebruikers'] = 'Handel'
    if column['Watergebruikers'] == '383100 ':
        df_watergebruik.loc[i, 'Watergebruikers'] = 'Vervoer en opslag'
    if column['Watergebruikers'] == '389100 ':
        df_watergebruik.loc[i, 'Watergebruikers'] = 'Horeca'
# Kolommen in de juiste volgorde zetten en hernoemen
df_watergebruik = df_watergebruik[['Jaar','Watergebruikers',
                 'TotaalLeidingwater_1','Drinkwater_2',
                 'Industriewater_3','TotaalGrondwater_4',
                 'GebruikVoorKoeling_5','OverigGebruikGrondwater_6',
                 'TotaalOppervlaktewater_7','ZoetOppervlaktewater_8',
                 'ZoutOppervlaktewater_9']]
df_watergebruik.rename(columns={'TotaalLeidingwater_1': 'Totaal_leidingwater_miljoen_m3',
                               'Drinkwater_2': 'Drinkwater_miljoen_m3',
                               'Industriewater_3': 'industriewater_miljoen_m3',
                               'TotaalGrondwater_4':'Totaal_grondwater_miljoen_m3',
                               'GebruikVoorKoeling_5':'Koelingwater_miljoen_m3',
                               'OverigGebruikGrondwater_6':'OverigeGebruikGrondwater_miljoen_m3',
                               'TotaalOppervlaktewater_7':'Totaal_oppervlaktewater_miljoen_m3',
                               'ZoetOppervlaktewater_8':'ZoetOppervlaktewater_miljoen_m3',
                               'ZoutOppervlaktewater_9':'ZoutOppervlaktewater_miljoen_m3'}, inplace=True)
#Jaar kolom converteren naar een datetime type
df_watergebruik['Jaar'] = pd.to_datetime(df_watergebruik['Jaar']).dt.date
df_watergebruik['Jaar'] = pd.to_datetime(df_watergebruik['Jaar']).dt.year
# Groeperen op gebruik per jaar
df_watergebruik = df_watergebruik[['Jaar','Watergebruikers',
                 'Totaal_leidingwater_miljoen_m3','Drinkwater_miljoen_m3',
                 'industriewater_miljoen_m3','Totaal_grondwater_miljoen_m3',
                 'Koelingwater_miljoen_m3','OverigeGebruikGrondwater_miljoen_m3',
                 'Totaal_oppervlaktewater_miljoen_m3','ZoetOppervlaktewater_miljoen_m3',
                 'ZoutOppervlaktewater_miljoen_m3']]
df_watergebruik['Totaal_gebruik'] = df_watergebruik['Totaal_leidingwater_miljoen_m3'] + df_watergebruik['Totaal_grondwater_miljoen_m3'] + df_watergebruik['Totaal_oppervlaktewater_miljoen_m3']
df_watergebruik_jaar = df_watergebruik.groupby(['Jaar'])['Totaal_leidingwater_miljoen_m3','Totaal_grondwater_miljoen_m3', 'Totaal_oppervlaktewater_miljoen_m3','Totaal_gebruik'].sum()
df_watergebruik_jaar['Totaal_gebruik_miljard_m3'] = df_watergebruik_jaar['Totaal_gebruik']/1000
df_totaal = df_watergebruik.groupby(['Jaar','Watergebruikers'])['Totaal_leidingwater_miljoen_m3','Totaal_grondwater_miljoen_m3','Totaal_oppervlaktewater_miljoen_m3'].sum()
#df_totaal[['Totaal_leidingwater_miljoen_m3','Totaal_grondwater_miljoen_m3','Totaal_oppervlaktewater_miljoen_m3']] = df_totaal[['Totaal_leidingwater_miljoen_m3','Totaal_grondwater_miljoen_m3','Totaal_oppervlaktewater_miljoen_m3']]/1000
df_totaal['Totaal_gebruik'] = df_totaal['Totaal_leidingwater_miljoen_m3'] + df_totaal['Totaal_grondwater_miljoen_m3'] + df_totaal['Totaal_oppervlaktewater_miljoen_m3']
df_totaal['Totaal_gebruik_miljard_m3'] = df_totaal['Totaal_gebruik']/1000
df_watergebruik_jaar = df_watergebruik_jaar.reset_index()
df_totaal = df_totaal.reset_index()
df_totaal_merge = df_totaal[['Jaar','Watergebruikers','Totaal_gebruik']]
# ## Voor het mergen moeten we alleen huishoudens,landbouw en infra gebruikers overhouden
Watergebruikers_particulier = ['Huishoudens','Landbouw','Vervoer en opslag']
df_totaal_merge1 = df_totaal_merge[df_totaal_merge['Watergebruikers'].isin(Watergebruikers_particulier)]
# ## Mergen van Bodemgebruik met Watergebruik
df_totaal_merge = bodemgebruik.merge(df_totaal_merge1, on ='Jaar', how = 'left')
df_totaal_merge = df_totaal_merge.assign(Totaal_oppervlak = lambda x: x['Water'] + x['Natuur']+x['Infra']+x['Bebouwd']+ x['Onverhard']+x['Landbouw'])
df_totaal_merge = df_totaal_merge.assign(Totaal_oppervlak_watergebruikers = lambda x: x['Infra']+x['Bebouwd']+x['Landbouw'])
df_totaal_merge = df_totaal_merge[['ID','Jaar','Watergebruikers','Locatie','Water','Natuur','Infra','Bebouwd','Onverhard','Landbouw','Totaal_gebruik','Totaal_oppervlak','Totaal_oppervlak_watergebruikers','geometry','centroid']]
# ## Het schrijven van een for-loop die zorgt voor een verdeling van water over de provincies aan de hand van het bodemgebruik
aantal_provincies = 12
df_totaal_merge['Totaal_gebruik_provincie'] = df_totaal_merge['Totaal_gebruik']/aantal_provincies

for i,column in df_totaal_merge.iterrows():
    if column['Watergebruikers'] == 'Landbouw':
        df_totaal_merge.loc[i,'percentage'] = column['Landbouw']/column['Totaal_oppervlak_watergebruikers']
    elif column['Watergebruikers'] == 'Vervoer en opslag':
        df_totaal_merge.loc[i,'percentage'] = column['Infra']/column['Totaal_oppervlak_watergebruikers']
    else :
        df_totaal_merge.loc[i,'percentage'] = column['Bebouwd']/column['Totaal_oppervlak_watergebruikers']
 
for i,column in df_totaal_merge.iterrows():
    if column['Watergebruikers'] == 'Landbouw':
        df_totaal_merge.loc[i,'Watergebruik_bodem_m3'] = column['percentage']*column['Totaal_gebruik_provincie']
    elif column['Watergebruikers'] == 'Vervoer en opslag':
        df_totaal_merge.loc[i,'Watergebruik_bodem_m3'] = column['percentage']*column['Totaal_gebruik_provincie']
    else :
        df_totaal_merge.loc[i,'Watergebruik_bodem_m3'] = column['percentage']*column['Totaal_gebruik_provincie']

df_totaal_merge_watergebruik = df_totaal_merge.groupby(['Jaar','Locatie'])['Watergebruik_bodem_m3'].sum().reset_index(name = 'Totaal_watergebruik_m3')
df_totaal_merge = df_totaal_merge[['Jaar','Locatie','Watergebruikers',
                                   'Water','Natuur','Infra','Bebouwd',
                                   'Onverhard','Landbouw','Totaal_gebruik',
                                  'Totaal_oppervlak_watergebruikers','Totaal_gebruik_provincie',
                                  'percentage','Watergebruik_bodem_m3']]
# ## Code voor het maken van de geospatial map
df_totaal_merge_map = df_totaal_merge[df_totaal_merge.Jaar == 2015]
df_totaal_merge_map = df_totaal_merge_map[['Jaar','Locatie','Water','Natuur','Infra','Bebouwd','Onverhard','Landbouw']]
df_totaal_merge_map = df_totaal_merge_map.groupby(['Jaar','Locatie'])['Water','Infra','Bebouwd','Natuur','Onverhard','Landbouw'].mean()
df_totaal_merge_map.reset_index(inplace = True)
Provincie_id = [1, 3, 6, 9, 12, 15, 18, 21, 24, 27, 30, 33]
df_totaal_merge_map['Provincie_id'] = Provincie_id



# ## Alle maps gemaakt per soort bodem
map_Natuur = folium.Map([52.0907374,5.1214201],zoom_start=7,zoom_control=False,
                   scrollWheelZoom=False,
                    max_zoom=7,
                    min_zoom=7,
                   dragging=False)

c_Natuur = folium.Choropleth(
    geo_data=geo_data1,
    name="choropleth",
    data=df_totaal_merge_map,
    columns=["Locatie", "Natuur"],
    key_on="feature.properties.Locatie",
    fill_color="YlGnBu",
    fill_opacity=0.85,
    line_opacity=0.2,
    legend_name="..",
)

for i in range(0,len(df_totaal_merge_map)):
    html= f"""
        <h2> {df_totaal_merge_map.iloc[i]['Locatie']}</h2>
        """
    iframe = folium.IFrame(html=html, width=900, height=1200)
    popup = folium.Popup(iframe, max_width=200)


folium.Marker(location=[52.0907374, 5.1214201],popup='<b>2843km2</b>',tooltip='Utrecht').add_to(map_Natuur)
folium.Marker(location=[51.9851034, 5.8987296],popup='<b>10125km2</b>',tooltip='Gelderland').add_to(map_Natuur)
folium.Marker(location=[53.2190652, 6.5680077],popup='<b>4739km2</b>',tooltip='Groningen').add_to(map_Natuur)
folium.Marker(location=[52.3638863, 6.4627523],popup='<b>6750km2</b>',tooltip='Overijssel').add_to(map_Natuur)
folium.Marker(location=[53.0949487, 5.8388679],popup='<b>3828km2</b>',tooltip='Friesland').add_to(map_Natuur)
folium.Marker(location=[52.6323813, 4.7533754],popup='<b>6096km2</b>',tooltip='Noord-Holland').add_to(map_Natuur)
folium.Marker(location=[52.078663, 4.288788],popup='<b>6083km2</b>',tooltip='Zuid-Holland').add_to(map_Natuur)
folium.Marker(location=[51.49694, 3.616689],popup='<b>3715km2</b>',tooltip='Zeeland').add_to(map_Natuur)
folium.Marker(location=[51.1913202, 5.9877715],popup='<b>4369km2</b>',tooltip='Limburg').add_to(map_Natuur)
folium.Marker(location=[52.8509512, 6.6057445],popup='<b>5321km2</b>',tooltip='Drenthe').add_to(map_Natuur)
folium.Marker(location=[52.518537, 5.471422],popup='<b>3828km2</b>',tooltip='Flevoland').add_to(map_Natuur)
folium.Marker(location=[51.555205, 5.078185],popup='<b>4369km2</b>',tooltip='Noord-Brabant').add_to(map_Natuur)


c_Natuur.add_to(map_Natuur)

map_Water = folium.Map([52.0907374,5.1214201],zoom_start=7,zoom_control=False,
                   scrollWheelZoom=False,
                    max_zoom=7,
                    min_zoom=7,
                   dragging=False)

c_Water = folium.Choropleth(
    geo_data=geo_data1,
    name="choropleth",
    data=df_totaal_merge_map,
    columns=["Locatie", "Water"],
    key_on="feature.properties.Locatie",
    fill_color="YlGnBu",
    fill_opacity=0.85,
    line_opacity=0.2,
    legend_name="..",
)

for i in range(0,len(df_totaal_merge_map)):
    html= f"""
        <h2> {df_totaal_merge_map.iloc[i]['Locatie']}</h2>
        """
    iframe = folium.IFrame(html=html, width=900, height=1200)
    popup = folium.Popup(iframe, max_width=200)


folium.Marker(location=[52.0907374, 5.1214201],popup='<b>2843km2</b>',tooltip='Utrecht').add_to(map_Water)
folium.Marker(location=[51.9851034, 5.8987296],popup='<b>10125km2</b>',tooltip='Gelderland').add_to(map_Water)
folium.Marker(location=[53.2190652, 6.5680077],popup='<b>4739km2</b>',tooltip='Groningen').add_to(map_Water)
folium.Marker(location=[52.3638863, 6.4627523],popup='<b>6750km2</b>',tooltip='Overijssel').add_to(map_Water)
folium.Marker(location=[53.0949487, 5.8388679],popup='<b>3828km2</b>',tooltip='Friesland').add_to(map_Water)
folium.Marker(location=[52.6323813, 4.7533754],popup='<b>6096km2</b>',tooltip='Noord-Holland').add_to(map_Water)
folium.Marker(location=[52.078663, 4.288788],popup='<b>6083km2</b>',tooltip='Zuid-Holland').add_to(map_Water)
folium.Marker(location=[51.49694, 3.616689],popup='<b>3715km2</b>',tooltip='Zeeland').add_to(map_Water)
folium.Marker(location=[51.1913202, 5.9877715],popup='<b>4369km2</b>',tooltip='Limburg').add_to(map_Water)
folium.Marker(location=[52.8509512, 6.6057445],popup='<b>5321km2</b>',tooltip='Drenthe').add_to(map_Water)
folium.Marker(location=[52.518537, 5.471422],popup='<b>3828km2</b>',tooltip='Flevoland').add_to(map_Water)
folium.Marker(location=[51.555205, 5.078185],popup='<b>4369km2</b>',tooltip='Noord-Brabant').add_to(map_Water)


c_Water.add_to(map_Water)

map_Infra = folium.Map([52.0907374,5.1214201],zoom_start=7,zoom_control=False,
                   scrollWheelZoom=False,
                    max_zoom=7,
                    min_zoom=7,
                   dragging=False)

c_Infra = folium.Choropleth(
    geo_data=geo_data1,
    name="choropleth",
    data=df_totaal_merge_map,
    columns=["Locatie", "Infra"],
    key_on="feature.properties.Locatie",
    fill_color="YlGnBu",
    fill_opacity=0.85,
    line_opacity=0.2,
    legend_name="..",
)

for i in range(0,len(df_totaal_merge_map)):
    html= f"""
        <h2> {df_totaal_merge_map.iloc[i]['Locatie']}</h2>
        """
    iframe = folium.IFrame(html=html, width=900, height=1200)
    popup = folium.Popup(iframe, max_width=200)


folium.Marker(location=[52.0907374, 5.1214201],popup='<b>2843km2</b>',tooltip='Utrecht').add_to(map_Infra)
folium.Marker(location=[51.9851034, 5.8987296],popup='<b>10125km2</b>',tooltip='Gelderland').add_to(map_Infra)
folium.Marker(location=[53.2190652, 6.5680077],popup='<b>4739km2</b>',tooltip='Groningen').add_to(map_Infra)
folium.Marker(location=[52.3638863, 6.4627523],popup='<b>6750km2</b>',tooltip='Overijssel').add_to(map_Infra)
folium.Marker(location=[53.0949487, 5.8388679],popup='<b>3828km2</b>',tooltip='Friesland').add_to(map_Infra)
folium.Marker(location=[52.6323813, 4.7533754],popup='<b>6096km2</b>',tooltip='Noord-Holland').add_to(map_Infra)
folium.Marker(location=[52.078663, 4.288788],popup='<b>6083km2</b>',tooltip='Zuid-Holland').add_to(map_Infra)
folium.Marker(location=[51.49694, 3.616689],popup='<b>3715km2</b>',tooltip='Zeeland').add_to(map_Infra)
folium.Marker(location=[51.1913202, 5.9877715],popup='<b>4369km2</b>',tooltip='Limburg').add_to(map_Infra)
folium.Marker(location=[52.8509512, 6.6057445],popup='<b>5321km2</b>',tooltip='Drenthe').add_to(map_Infra)
folium.Marker(location=[52.518537, 5.471422],popup='<b>3828km2</b>',tooltip='Flevoland').add_to(map_Infra)
folium.Marker(location=[51.555205, 5.078185],popup='<b>4369km2</b>',tooltip='Noord-Brabant').add_to(map_Infra)


c_Infra.add_to(map_Infra)

map_Bebouwd = folium.Map([52.0907374,5.1214201],zoom_start=7,zoom_control=False,
                   scrollWheelZoom=False,
                    max_zoom=7,
                    min_zoom=7,
                   dragging=False)

c_Bebouwd = folium.Choropleth(
    geo_data=geo_data1,
    name="choropleth",
    data=df_totaal_merge_map,
    columns=["Locatie", "Bebouwd"],
    key_on="feature.properties.Locatie",
    fill_color="YlGnBu",
    fill_opacity=0.85,
    line_opacity=0.2,
    legend_name="..",
)

for i in range(0,len(df_totaal_merge_map)):
    html= f"""
        <h2> {df_totaal_merge_map.iloc[i]['Locatie']}</h2>
        """
    iframe = folium.IFrame(html=html, width=900, height=1200)
    popup = folium.Popup(iframe, max_width=200)


folium.Marker(location=[52.0907374, 5.1214201],popup='<b>2843km2</b>',tooltip='Utrecht').add_to(map_Bebouwd)
folium.Marker(location=[51.9851034, 5.8987296],popup='<b>10125km2</b>',tooltip='Gelderland').add_to(map_Bebouwd)
folium.Marker(location=[53.2190652, 6.5680077],popup='<b>4739km2</b>',tooltip='Groningen').add_to(map_Bebouwd)
folium.Marker(location=[52.3638863, 6.4627523],popup='<b>6750km2</b>',tooltip='Overijssel').add_to(map_Bebouwd)
folium.Marker(location=[53.0949487, 5.8388679],popup='<b>3828km2</b>',tooltip='Friesland').add_to(map_Bebouwd)
folium.Marker(location=[52.6323813, 4.7533754],popup='<b>6096km2</b>',tooltip='Noord-Holland').add_to(map_Bebouwd)
folium.Marker(location=[52.078663, 4.288788],popup='<b>6083km2</b>',tooltip='Zuid-Holland').add_to(map_Bebouwd)
folium.Marker(location=[51.49694, 3.616689],popup='<b>3715km2</b>',tooltip='Zeeland').add_to(map_Bebouwd)
folium.Marker(location=[51.1913202, 5.9877715],popup='<b>4369km2</b>',tooltip='Limburg').add_to(map_Bebouwd)
folium.Marker(location=[52.8509512, 6.6057445],popup='<b>5321km2</b>',tooltip='Drenthe').add_to(map_Bebouwd)
folium.Marker(location=[52.518537, 5.471422],popup='<b>3828km2</b>',tooltip='Flevoland').add_to(map_Bebouwd)
folium.Marker(location=[51.555205, 5.078185],popup='<b>4369km2</b>',tooltip='Noord-Brabant').add_to(map_Bebouwd)


c_Bebouwd.add_to(map_Bebouwd)

map_Onverhard = folium.Map([52.0907374,5.1214201],zoom_start=7,zoom_control=False,
                   scrollWheelZoom=False,
                    max_zoom=7,
                    min_zoom=7,
                   dragging=False)

c_Onverhard = folium.Choropleth(
    geo_data=geo_data1,
    name="choropleth",
    data=df_totaal_merge_map,
    columns=["Locatie", "Onverhard"],
    key_on="feature.properties.Locatie",
    fill_color="YlGnBu",
    fill_opacity=0.85,
    line_opacity=0.2,
    legend_name="..",
)

for i in range(0,len(df_totaal_merge_map)):
    html= f"""
        <h2> {df_totaal_merge_map.iloc[i]['Locatie']}</h2>
        """
    iframe = folium.IFrame(html=html, width=900, height=1200)
    popup = folium.Popup(iframe, max_width=200)


folium.Marker(location=[52.0907374, 5.1214201],popup='<b>2843km2</b>',tooltip='Utrecht').add_to(map_Onverhard)
folium.Marker(location=[51.9851034, 5.8987296],popup='<b>10125km2</b>',tooltip='Gelderland').add_to(map_Onverhard)
folium.Marker(location=[53.2190652, 6.5680077],popup='<b>4739km2</b>',tooltip='Groningen').add_to(map_Onverhard)
folium.Marker(location=[52.3638863, 6.4627523],popup='<b>6750km2</b>',tooltip='Overijssel').add_to(map_Onverhard)
folium.Marker(location=[53.0949487, 5.8388679],popup='<b>3828km2</b>',tooltip='Friesland').add_to(map_Onverhard)
folium.Marker(location=[52.6323813, 4.7533754],popup='<b>6096km2</b>',tooltip='Noord-Holland').add_to(map_Onverhard)
folium.Marker(location=[52.078663, 4.288788],popup='<b>6083km2</b>',tooltip='Zuid-Holland').add_to(map_Onverhard)
folium.Marker(location=[51.49694, 3.616689],popup='<b>3715km2</b>',tooltip='Zeeland').add_to(map_Onverhard)
folium.Marker(location=[51.1913202, 5.9877715],popup='<b>4369km2</b>',tooltip='Limburg').add_to(map_Onverhard)
folium.Marker(location=[52.8509512, 6.6057445],popup='<b>5321km2</b>',tooltip='Drenthe').add_to(map_Onverhard)
folium.Marker(location=[52.518537, 5.471422],popup='<b>3828km2</b>',tooltip='Flevoland').add_to(map_Onverhard)
folium.Marker(location=[51.555205, 5.078185],popup='<b>4369km2</b>',tooltip='Noord-Brabant').add_to(map_Onverhard)


c_Onverhard.add_to(map_Onverhard)

map_Landbouw = folium.Map([52.0907374,5.1214201],zoom_start=7,zoom_control=False,
                   scrollWheelZoom=False,
                    max_zoom=7,
                    min_zoom=7,
                   dragging=False)

c_Landbouw = folium.Choropleth(
    geo_data=geo_data1,
    name="choropleth",
    data=df_totaal_merge_map,
    columns=["Locatie", "Landbouw"],
    key_on="feature.properties.Locatie",
    fill_color="YlGnBu",
    fill_opacity=0.85,
    line_opacity=0.2,
    legend_name="..",
)

for i in range(0,len(df_totaal_merge_map)):
    html= f"""
        <h2> {df_totaal_merge_map.iloc[i]['Locatie']}</h2>
        """
    iframe = folium.IFrame(html=html, width=900, height=1200)
    popup = folium.Popup(iframe, max_width=200)


folium.Marker(location=[52.0907374, 5.1214201],popup='<b>2843km2</b>',tooltip='Utrecht').add_to(map_Landbouw)
folium.Marker(location=[51.9851034, 5.8987296],popup='<b>10125km2</b>',tooltip='Gelderland').add_to(map_Landbouw)
folium.Marker(location=[53.2190652, 6.5680077],popup='<b>4739km2</b>',tooltip='Groningen').add_to(map_Landbouw)
folium.Marker(location=[52.3638863, 6.4627523],popup='<b>6750km2</b>',tooltip='Overijssel').add_to(map_Landbouw)
folium.Marker(location=[53.0949487, 5.8388679],popup='<b>3828km2</b>',tooltip='Friesland').add_to(map_Landbouw)
folium.Marker(location=[52.6323813, 4.7533754],popup='<b>6096km2</b>',tooltip='Noord-Holland').add_to(map_Landbouw)
folium.Marker(location=[52.078663, 4.288788],popup='<b>6083km2</b>',tooltip='Zuid-Holland').add_to(map_Landbouw)
folium.Marker(location=[51.49694, 3.616689],popup='<b>3715km2</b>',tooltip='Zeeland').add_to(map_Landbouw)
folium.Marker(location=[51.1913202, 5.9877715],popup='<b>4369km2</b>',tooltip='Limburg').add_to(map_Landbouw)
folium.Marker(location=[52.8509512, 6.6057445],popup='<b>5321km2</b>',tooltip='Drenthe').add_to(map_Landbouw)
folium.Marker(location=[52.518537, 5.471422],popup='<b>3828km2</b>',tooltip='Flevoland').add_to(map_Landbouw)
folium.Marker(location=[51.555205, 5.078185],popup='<b>4369km2</b>',tooltip='Noord-Brabant').add_to(map_Landbouw)


c_Landbouw.add_to(map_Landbouw)
# ## Toekomstig model
df_model = df_watergebruik.groupby(['Jaar'])['Totaal_gebruik'].sum().reset_index()
Nieuwe_rij1 = {'Jaar':'2025', 'Totaal_gebruik': 16379.4} 
Nieuwe_rij2 = {'Jaar':'2035', 'Totaal_gebruik': 18545.9}
Nieuwe_rij3 = {'Jaar':'2050', 'Totaal_gebruik': 22344.7}

df_watergebruik_jaar_toekomst1 = df_model.append(Nieuwe_rij1, ignore_index=True)
df_watergebruik_jaar_toekomst2 = df_watergebruik_jaar_toekomst1.append(Nieuwe_rij2, ignore_index=True)
df_model = df_watergebruik_jaar_toekomst2.append(Nieuwe_rij3, ignore_index=True)
df_model['Jaar'] = pd.to_datetime(df_model['Jaar'], format = '%Y')
df_model['Jaar'] = df_model['Jaar'].dt.year
fig_model = px.scatter(df_model, x = 'Jaar', y = 'Totaal_gebruik',trendline='rolling', trendline_options=dict(window=3))
# ## Streamlit Code

# ### Achtergrond invoegen
def add_bg_from_url():
    st.markdown(
         f"""
         <style>
         .stApp {{
             background-image: url(https://img.freepik.com/premium-photo/eenvoudige-witte-achtergrond-met-vloeiende-lijnen-in-lichte-kleuren_476363-5558.jpg?w=1380);
             background-attachment: fixed;
             background-size: cover;
             #background-opacity: 0.3
         }}
         </style>
         """,
         unsafe_allow_html=True
     )

add_bg_from_url() 


pages = st.sidebar.selectbox('Pagina' ,('Home','Bodemgebruik in cijfers','Bodemgebruik','Watergebruik', 'Verloop van het Watergebruik', 'Toekomstig watergebruik'))
st.sidebar.markdown('**Gemaakt door**: Giel Suweijn en Roy Pontman',unsafe_allow_html=True)
st.sidebar.markdown('              Minor Data Science')
st.sidebar.markdown('              Hogeschool van Amsterdam (HVA)')
st.sidebar.markdown('              November 2022')
if pages == 'Home':
    st.title("**Bodem- en watergebruik in Nederland**")
    st.markdown("Met dit dashboard wordt geprobeerd het bodem- en watergebruik in Nederland in kaart te krijgen. Door middel van datasets van CBS zijn jaargebruiken opgehaald en geanalyseerd. In de linker ribbon kunt u zich bewegen door het dashboard door middel van een dropdown. In deze dropdown is er een keuze te maken tussen het bodemgebruik, het watergebruik, het verloop van het watergebruik en het toekomstige watergebruik.")
    image = Image.open('Water.jpg')
    st.image(image, caption='De basis is water',width = 600)
    image = Image.open('Bodem.jpg')
    st.image(image, caption='Complexe indeling in Nederland',width =600)
    st.markdown("**Bronnen**:",unsafe_allow_html=True)
    st.markdown("__Watergebruik__: https://opendata.cbs.nl/statline/portal.html?_la=nl&_catalog=CBS&tableId=82883NED&_theme=233",unsafe_allow_html=True)
    st.markdown("__Bodemgebruik__: https://opendata.cbs.nl/statline/portal.html?_catalog=CBS&_la=nl&tableId=37105&_theme=303",unsafe_allow_html=True)
    


elif pages == 'Bodemgebruik in cijfers':
    st.subheader('Bodemgebruik per jaar')
    st.markdown('In onderstaand veld kunt u een jaar invullen waarin u het bodemgebruik kunt zien per provincie.')
    st.markdown('De jaren beschikbaar voor het bodemgebruik zijn: 2003, 2006, 2008, 2010, 2012 en 2015In onderstaand veld kunt u een jaar invullen waarin u het bodemgebruik kunt zien per provincie.')
    #Knoppen maken zodat een dag van het jaar gekozen kan worden
    number = st.number_input('Voer een jaar in', min_value=df_watergebruik.Jaar.min(), max_value= df_watergebruik.Jaar.max(), value=2003, step=1)
    df_totaal_merge = df_totaal_merge.loc[df_totaal_merge['Jaar'] == number]
    st.markdown('Vervolgens kunt u door middel van een dropdown bepalen welk soort bodemgebruik u wilt zien:')
    #Dropdown maken zodat het soort watergebruik gekozen kan worden
    keuze = st.selectbox( 'Bodemgebruik', ('Water',"Natuur",'Infra',
                                                    'Bebouwd','Onverhard','Landbouw'))
                                                   
    st.markdown('Na u keuze komt een tabel naar voren van het bodemgebruik per provincie.')
    st.markdown('Daarnaast wordt een grafiek zichtbaar met het gebruik per gekozen jaar per sector')
    
    if keuze == 'Water':
        st.subheader('Wateroppervlak in Nederland')
        df_totaal_merge = df_totaal_merge.groupby(['Jaar','Locatie'])['Water'].mean().reset_index(name = 'Water')
        with st.expander("Zie het tabel"):
            st.dataframe(df_totaal_merge[['Locatie','Water']])
      #Figuur maken van de keuze
        figbodem = px.bar(df_totaal_merge, x = 'Jaar', y= 'Water', text_auto=True, color = 'Locatie', opacity = 0.6, barmode='group')
        figbodem.update_layout({'updatemenus':[dict(
                 buttons=[
                     dict(label="Linear",  
                          method="relayout", 
                          args=[{"yaxis.type": "linear"}]),
                     dict(label="Log", 
                          method="relayout", 
                          args=[{"yaxis.type": "log"}])]
                  )]}, height = 700, width = 700,
                  title='Wateroppervlak per provincie', yaxis_title = "Wateroppervlak in km^2")
      
      # Verdeling maken van aandeel per sector
        figbodem1 = px.pie(df_totaal_merge, values='Water', names='Locatie', opacity = 0.7, title='Aandeel wateroppervlak per provincie')
        figbodem1.update_traces(textinfo='percent+label')
        with st.expander("Zie de Visualisaties"):
            st.plotly_chart(figbodem)
            st.plotly_chart(figbodem1)
            st.write("""
              De grafieken laten zien dat Flevoland, Friesland en Noord-Holland het meeste wateroppervlak hebben in Nederland.
              """)
    if keuze == 'Natuur':
        st.subheader('Natuur oppervlak in Nederland')
        df_totaal_merge = df_totaal_merge.groupby(['Jaar','Locatie'])['Natuur'].mean().reset_index(name = 'Natuur')
        with st.expander("Zie het tabel"):
            st.dataframe(df_totaal_merge[['Locatie','Natuur']])
      #Figuur maken van de keuze
        figbodem = px.bar(df_totaal_merge, x = 'Jaar', y= 'Natuur', text_auto=True, color = 'Locatie', opacity = 0.6, barmode='group')
        figbodem.update_layout({'updatemenus':[dict(
                 buttons=[
                     dict(label="Linear",  
                          method="relayout", 
                          args=[{"yaxis.type": "linear"}]),
                     dict(label="Log", 
                          method="relayout", 
                          args=[{"yaxis.type": "log"}])]
                  )]}, height = 700, width = 700,
                  title='Natuur oppervlak per provincie', yaxis_title = "Natuur oppervlak in km^2")
      
      # Verdeling maken van aandeel per sector
        figbodem1 = px.pie(df_totaal_merge, values='Natuur', names='Locatie', opacity = 0.7, title='Aandeel natuur oppervlak per provincie')
        figbodem1.update_traces(textinfo='percent+label')
        with st.expander("Zie de Visualisaties"):
            st.plotly_chart(figbodem)
            st.plotly_chart(figbodem1)
            st.write("""
              De grafieken laten zien dat Gelderland en Noord-Brabant het meeste natuur oppervlak hebben in Nederland.
              """)   
    if keuze == 'Infra':
        st.subheader('Infrastructuur oppervlak in Nederland')
        df_totaal_merge = df_totaal_merge.groupby(['Jaar','Locatie'])['Infra'].mean().reset_index(name = 'Infra')
        with st.expander("Zie het tabel"):
            st.dataframe(df_totaal_merge[['Locatie','Infra']])
      #Figuur maken van de keuze
        figbodem = px.bar(df_totaal_merge, x = 'Jaar', y= 'Infra', text_auto=True, color = 'Locatie', opacity = 0.6, barmode='group')
        figbodem.update_layout({'updatemenus':[dict(
                 buttons=[
                     dict(label="Linear",  
                          method="relayout", 
                          args=[{"yaxis.type": "linear"}]),
                     dict(label="Log", 
                          method="relayout", 
                          args=[{"yaxis.type": "log"}])]
                  )]}, height = 700, width = 700,
                  title='Infrastructuur oppervlak per provincie', yaxis_title = "Infrastructuur oppervlak in km^2")
      
      # Verdeling maken van aandeel per sector
        figbodem1 = px.pie(df_totaal_merge, values='Infra', names='Locatie', opacity = 0.7, title='Aandeel infrastructuur oppervlak per provincie')
        figbodem1.update_traces(textinfo='percent+label')
        with st.expander("Zie de Visualisaties"):
            st.plotly_chart(figbodem)
            st.plotly_chart(figbodem1)
            st.write("""
              De grafieken laten zien dat Gelderland en Noord-Brabant het meeste infrastructuur oppervlak hebben in Nederland.
              """)   
    if keuze == 'Bebouwd':
        st.subheader('Bebouwd oppervlak in Nederland')
        df_totaal_merge = df_totaal_merge.groupby(['Jaar','Locatie'])['Bebouwd'].mean().reset_index(name = 'Bebouwd')
        with st.expander("Zie het tabel"):
            st.dataframe(df_totaal_merge[['Locatie','Bebouwd']])
      #Figuur maken van de keuze
        figbodem = px.bar(df_totaal_merge, x = 'Jaar', y= 'Bebouwd', text_auto=True, color = 'Locatie', opacity = 0.6, barmode='group')
        figbodem.update_layout({'updatemenus':[dict(
                 buttons=[
                     dict(label="Linear",  
                          method="relayout", 
                          args=[{"yaxis.type": "linear"}]),
                     dict(label="Log", 
                          method="relayout", 
                          args=[{"yaxis.type": "log"}])]
                  )]}, height = 700, width = 700,
                  title='Bebouwd oppervlak per provincie', yaxis_title = "Bebouwd oppervlak in km^2")
      
      # Verdeling maken van aandeel per sector
        figbodem1 = px.pie(df_totaal_merge, values='Bebouwd', names='Locatie', opacity = 0.7, title='Aandeel Bebouwd oppervlak per provincie')
        figbodem1.update_traces(textinfo='percent+label')
        with st.expander("Zie de Visualisaties"):
            st.plotly_chart(figbodem)
            st.plotly_chart(figbodem1)
            st.write("""
              De grafieken laten zien dat Zuid-Holland en Noord-Brabant het meeste bebouwd oppervlak hebben in Nederland.
              """)
    if keuze == 'Onverhard':
        st.subheader('Onverhard oppervlak in Nederland')
        df_totaal_merge = df_totaal_merge.groupby(['Jaar','Locatie'])['Onverhard'].mean().reset_index(name = 'Onverhard')
        with st.expander("Zie het tabel"):
            st.dataframe(df_totaal_merge[['Locatie','Onverhard']])
      #Figuur maken van de keuze
        figbodem = px.bar(df_totaal_merge, x = 'Jaar', y= 'Onverhard', text_auto=True, color = 'Locatie', opacity = 0.6, barmode='group')
        figbodem.update_layout({'updatemenus':[dict(
                 buttons=[
                     dict(label="Linear",  
                          method="relayout", 
                          args=[{"yaxis.type": "linear"}]),
                     dict(label="Log", 
                          method="relayout", 
                          args=[{"yaxis.type": "log"}])]
                  )]}, height = 700, width = 700,
                  title='Onverhard oppervlak per provincie', yaxis_title = "Onverhard oppervlak in km^2")
      
      # Verdeling maken van aandeel per sector
        figbodem1 = px.pie(df_totaal_merge, values='Onverhard', names='Locatie', opacity = 0.7, title='Aandeel Onverhard oppervlak per provincie')
        figbodem1.update_traces(textinfo='percent+label')
        with st.expander("Zie de Visualisaties"):
            st.plotly_chart(figbodem)
            st.plotly_chart(figbodem1)
            st.write("""
              De grafieken laten zien dat Zuid-Holland, Noord-Holland, Gelderland en Noord Brabant het meeste onverhard oppervlak hebben in Nederland.
              """)
            
    if keuze == 'Landbouw':
        st.subheader('Landbouw oppervlak in Nederland')
        df_totaal_merge = df_totaal_merge.groupby(['Jaar','Locatie'])['Landbouw'].mean().reset_index(name = 'Landbouw')
        with st.expander("Zie het tabel"):
            st.dataframe(df_totaal_merge[['Locatie','Landbouw']])
      #Figuur maken van de keuze
        figbodem = px.bar(df_totaal_merge, x = 'Jaar', y= 'Landbouw', text_auto=True, color = 'Locatie', opacity = 0.6, barmode='group')
        figbodem.update_layout({'updatemenus':[dict(
                 buttons=[
                     dict(label="Linear",  
                          method="relayout", 
                          args=[{"yaxis.type": "linear"}]),
                     dict(label="Log", 
                          method="relayout", 
                          args=[{"yaxis.type": "log"}])]
                  )]}, height = 700, width = 700,
                  title='Landbouw oppervlak per provincie', yaxis_title = "Landbouw oppervlak in km^2")
      
      # Verdeling maken van aandeel per sector
        figbodem1 = px.pie(df_totaal_merge, values='Landbouw', names='Locatie', opacity = 0.7, title='Aandeel Landbouw oppervlak per provincie')
        figbodem1.update_traces(textinfo='percent+label')
        with st.expander("Zie de Visualisaties"):
            st.plotly_chart(figbodem)
            st.plotly_chart(figbodem1)
            st.write("""
              De grafieken laten zien dat Gelderland en Noord Brabant het meeste landbouw oppervlak hebben in Nederland.
              """)
elif pages == 'Bodemgebruik':
    st.subheader('Bodemgebruik in Nederland')
    st.markdown('Onder het kopje "Bodemgebruik in cijfers" was te zien het bodemgebruik per soort bodem per provincie in Nederland.')
    st.markdown('Op deze pagina wordt het gebruik zichtbaar gemaakt via een kaart')
    st.markdown('Onderstaand is een selectbox te zien waarin een type bodem geselecteerd kan worden. De map die eruit komt is de meest recente oppervlakte.')
    keuze = st.selectbox( 'Bodemgebruik', ('Water',"Natuur",'Infra',
                                                    'Bebouwd','Onverhard','Landbouw'))
    if keuze == 'Water':
      st.subheader('Wateroppervlak in Nederland')
      folium_static(map_Water)
    if keuze == 'Natuur':
      st.subheader('Natuur oppervlak in Nederland')
      folium_static(map_Natuur)
    if keuze == 'Infra':
      st.subheader('Infrastructuur oppervlak in Nederland')
      folium_static(map_Infra)
    if keuze == 'Bebouwd':
      st.subheader('Bebouwd oppervlak in Nederland')
      folium_static(map_Bebouwd)
    if keuze == 'Onverhard':
      st.subheader('Onverhard oppervlak in Nederland')
      folium_static(map_Onverhard)
    if keuze == 'Landbouw':
      st.subheader('Landbouw oppervlak in Nederland')
      folium_static(map_Landbouw)
      
elif pages == 'Watergebruik':
    st.subheader('Watergebruik per jaar')
    st.markdown('In onderstaand veld kunt u een jaar invullen waarin u het watergebruik kunt zien per soort water.')
    st.markdown('Daarnaast is er data bekend vanaf 2003 tot en met 2020.')
    #Knoppen maken zodat een dag van het jaar gekozen kan worden
    number = st.number_input('Voer een jaar in', min_value=df_watergebruik.Jaar.min(), max_value= df_watergebruik.Jaar.max(), value=2003, step=1)
    df_watergebruik = df_watergebruik.loc[df_watergebruik['Jaar'] == number]
    df_watergebruik.reset_index(inplace=True,drop=True)
    st.markdown('Vervolgens kunt u door middel van een dropdown bepalen welk soort watergebruik u wilt zien:')
    #Dropdown maken zodat het soort watergebruik gekozen kan worden
    keuze = st.selectbox( 'Gebruik soort water', ('Totaal leidingwater',"Drinkwater",'Industriewater',
                                                    'Totaal grondwater','Koelingwater','Overige gebruik grondwater',
                                                   'Totaal oppervlaktewater','Zoet oppervlaktewater','Zout oppervlaktewater'))
    st.markdown('Na u keuze komt een tabel naar voren van het soort water met daarbij de watergebruikers. Deze watergebruikers zijn gekozen sectoren in Nederland die ons leuk leek om weer te kunnen geven.')
    st.markdown('Daarnaast wordt een grafiek zichtbaar met het gebruik per gekozen jaar per sector')
    if keuze == 'Totaal leidingwater':
      st.subheader('Totaal leidingwater')
      df_watergebruik['Totaal_leidingwater_miljoen_m3'] = np.around(df_watergebruik['Totaal_leidingwater_miljoen_m3'], decimals=2)
      with st.expander("Zie het tabel"):
        st.dataframe(df_watergebruik[['Watergebruikers','Totaal_leidingwater_miljoen_m3']])
      #Figuur maken van de keuze
      fig2 = px.bar(df_watergebruik, x = 'Jaar', y= 'Totaal_leidingwater_miljoen_m3', text_auto=True, color = 'Watergebruikers', opacity = 0.6, barmode='group')
      fig2.update_layout({'updatemenus':[dict(
                 buttons=[
                     dict(label="Linear",  
                          method="relayout", 
                          args=[{"yaxis.type": "linear"}]),
                     dict(label="Log", 
                          method="relayout", 
                          args=[{"yaxis.type": "log"}])]
                  )]}, height = 700, width = 700,
                  title='Totaal watergebruik voor Leidingwater', yaxis_title = "Leidingwater gebruik in miljoen m3")
      
      # Verdeling maken van aandeel per sector
      fig = px.pie(df_watergebruik, values='Totaal_leidingwater_miljoen_m3', names='Watergebruikers', opacity = 0.7, title='Aandeel leidingwatergebruik per sector')
      fig.update_traces(textinfo='percent+label')
      with st.expander("Zie de Visualisaties"):
        st.plotly_chart(fig2)
        st.plotly_chart(fig)
        st.write("""
          De grafieken laten zien dat huishoudens en Industrie veruit het meeste leidingwater gebruiken in Nederland.
          """)   

      
      
    if keuze == 'Drinkwater':
      st.subheader('Drinkwater')
      df_watergebruik['Drinkwater_miljoen_m3'] = np.around(df_watergebruik['Drinkwater_miljoen_m3'], decimals=2)
      with st.expander("Zie het tabel"):
        st.dataframe(df_watergebruik[['Watergebruikers','Drinkwater_miljoen_m3']])

      #Figuur maken van de keuze
      fig2 = px.bar(df_watergebruik, x = 'Jaar', y= 'Drinkwater_miljoen_m3', text_auto=True, color = 'Watergebruikers', opacity = 0.6, barmode='group')
      fig2.update_layout({'updatemenus':[dict(
                 buttons=[
                     dict(label="Linear",  
                          method="relayout", 
                          args=[{"yaxis.type": "linear"}]),
                     dict(label="Log", 
                          method="relayout", 
                          args=[{"yaxis.type": "log"}])]
                  )]}, height = 700, width = 700,
                  title='Totaal watergebruik voor Drinkwater', yaxis_title = "Drinkwater gebruik in miljoen m3")
      # Verdeling maken van aandeel per sector
      fig = px.pie(df_watergebruik, values='Drinkwater_miljoen_m3', names='Watergebruikers', opacity = 0.7, title='Aandeel drinkwatergebruik per sector')
      fig.update_traces(textinfo='percent+label')
      with st.expander("Zie de Visualisaties"):
        st.plotly_chart(fig2)
        st.plotly_chart(fig)
        st.write("""
          De visualisaties laten zien dat Huishoudens en de Industrie veruit het meeste drinkwater gebruiken in Nederland.
          """)         
      
    if keuze == 'Industriewater':
      st.subheader('Industriewater')
      df_watergebruik['industriewater_miljoen_m3'] = np.around(df_watergebruik['industriewater_miljoen_m3'].tolist(), decimals=2)
      with st.expander("Zie het tabel"):
        st.dataframe(df_watergebruik[['Watergebruikers','industriewater_miljoen_m3']])

      #Figuur maken van de keuze
      fig2 = px.bar(df_watergebruik, x = 'Jaar', y= 'industriewater_miljoen_m3', text_auto=True, color = 'Watergebruikers', opacity = 0.6, barmode='group')
      fig2.update_layout({'updatemenus':[dict(
                 buttons=[
                     dict(label="Linear",  
                          method="relayout", 
                          args=[{"yaxis.type": "linear"}]),
                     dict(label="Log", 
                          method="relayout", 
                          args=[{"yaxis.type": "log"}])]
                  )]}, height = 700, width = 700,
                  title='Totaal watergebruik voor Industriewater', yaxis_title = "Industriewater gebruik in miljoen m3")
      # Verdeling maken van aandeel per sector
      fig = px.pie(df_watergebruik, values='industriewater_miljoen_m3', names='Watergebruikers', opacity = 0.7, title='Aandeel Industriewatergebruik per sector')
      fig.update_traces(textinfo='percent+label')
      with st.expander("Zie de Visualisaties"):
        st.plotly_chart(fig2)
        st.plotly_chart(fig)
        st.write("""
          De visualisaties laten zien dat de Industrie de enige sector is die industriewater gebruikt in Nederland.
          """)
      
    if keuze == 'Totaal grondwater':
      st.subheader('Totaal grondwater')
      df_watergebruik['Totaal_grondwater_miljoen_m3'] = np.around(df_watergebruik['Totaal_grondwater_miljoen_m3'], decimals=2)
      with st.expander("Zie het tabel"):
        st.dataframe(df_watergebruik[['Watergebruikers','Totaal_grondwater_miljoen_m3']])

      #Figuur maken van de keuze
      fig2 = px.bar(df_watergebruik, x = 'Jaar', y= 'Totaal_grondwater_miljoen_m3', text_auto=True, color = 'Watergebruikers', opacity = 0.6, barmode='group')
      fig2.update_layout({'updatemenus':[dict(
                 buttons=[
                     dict(label="Linear",  
                          method="relayout", 
                          args=[{"yaxis.type": "linear"}]),
                     dict(label="Log", 
                          method="relayout", 
                          args=[{"yaxis.type": "log"}])]
                  )]}, height = 700, width = 700,
                  title='Totaal watergebruik voor Grondwater', yaxis_title = "Grondwater gebruik in miljoen m3")
      # Verdeling maken van aandeel per sector
      fig = px.pie(df_watergebruik, values='Totaal_grondwater_miljoen_m3', names='Watergebruikers', opacity = 0.7, title='Aandeel Grondwatergebruik per sector')
      fig.update_traces(textinfo='percent+label')
      with st.expander("Zie de Visualisaties"):
        st.plotly_chart(fig2)
        st.plotly_chart(fig)
        st.write("""
          De visualisaties laten zien dat de Water- en afval sector, Industrie, Voedselwinning en de Landbouwsector veruit het meeste grondwater gebruiken in Nederland.
          """)
      
    if keuze == 'Koelingwater':
      st.subheader('Koelingwater')
      df_watergebruik['Koelingwater_miljoen_m3'] = np.around(df_watergebruik['Koelingwater_miljoen_m3'], decimals=2)
      with st.expander("Zie het tabel"):
        st.dataframe(df_watergebruik[['Watergebruikers','Koelingwater_miljoen_m3']])

      #Figuur maken van de keuze
      fig2 = px.bar(df_watergebruik, x = 'Jaar', y= 'Koelingwater_miljoen_m3', text_auto=True, color = 'Watergebruikers', opacity = 0.6, barmode='group')
      fig2.update_layout({'updatemenus':[dict(
                 buttons=[
                     dict(label="Linear",  
                          method="relayout", 
                          args=[{"yaxis.type": "linear"}]),
                     dict(label="Log", 
                          method="relayout", 
                          args=[{"yaxis.type": "log"}])]
                  )]}, height = 700, width = 700,
                  title='Totaal watergebruik voor Koelwater', yaxis_title = "Koelwater gebruik in miljoen m3")
      # Verdeling maken van aandeel per sector
      fig = px.pie(df_watergebruik, values='Koelingwater_miljoen_m3', names='Watergebruikers', opacity = 0.7, title='Aandeel Koelwatergebruik per sector')
      fig.update_traces(textinfo='percent+label')
      with st.expander("Zie de Visualisaties"):
        st.plotly_chart(fig2)
        st.plotly_chart(fig)
        st.write("""
          De visualisaties laten zien dat de Industrie en de Voedelwinning sector veruit het meeste koelwater gebruiken in Nederland.
          """)
      
    if keuze == 'Overige gebruik grondwater':
      st.subheader('Overige gebruik grondwater')
      df_watergebruik['OverigeGebruikGrondwater_miljoen_m3'] = np.around(df_watergebruik['OverigeGebruikGrondwater_miljoen_m3'], decimals=2)
      with st.expander("Zie het tabel"):
        st.dataframe(df_watergebruik[['Watergebruikers','OverigeGebruikGrondwater_miljoen_m3']])

      #Figuur maken van de keuze
      fig2 = px.bar(df_watergebruik, x = 'Jaar', y= 'OverigeGebruikGrondwater_miljoen_m3', text_auto=True, color = 'Watergebruikers', opacity = 0.6, barmode='group')
      fig2.update_layout({'updatemenus':[dict(
                 buttons=[
                     dict(label="Linear",  
                          method="relayout", 
                          args=[{"yaxis.type": "linear"}]),
                     dict(label="Log", 
                          method="relayout", 
                          args=[{"yaxis.type": "log"}])]
                  )]}, height = 700, width = 700,
                  title='Totaal grondwatergebruik voor overige doeleinde', yaxis_title = "Overige gebruik grondwater in miljoen m3")
      # Verdeling maken van aandeel per sector
      fig = px.pie(df_watergebruik, values='OverigeGebruikGrondwater_miljoen_m3', names='Watergebruikers', opacity = 0.7, title='Aandeel Overig grondwatergebruik per sector')
      fig.update_traces(textinfo='percent+label')
      with st.expander("Zie de Visualisaties"):
        st.plotly_chart(fig2)
        st.plotly_chart(fig)
        st.write("""
          De visualisaties laten zien dat de Water- en afval sector en de Landbouwsector veruit het meeste grondwater gebruiken in Nederland. Zonder daarmee Koelwater mee te rekenen.
          """)
      
    if keuze == 'Totaal oppervlaktewater':
      st.subheader('Totaal oppervlaktewater')
      df_watergebruik['Totaal_oppervlaktewater_miljoen_m3'] = np.around(df_watergebruik['Totaal_oppervlaktewater_miljoen_m3'], decimals=2)
      with st.expander("Zie het tabel"):
        st.dataframe(df_watergebruik[['Watergebruikers','Totaal_oppervlaktewater_miljoen_m3']])

      #Figuur maken van de keuze
      fig2 = px.bar(df_watergebruik, x = 'Jaar', y= 'Totaal_oppervlaktewater_miljoen_m3', text_auto=True, color = 'Watergebruikers', opacity = 0.6, barmode='group')
      fig2.update_layout({'updatemenus':[dict(
                 buttons=[
                     dict(label="Linear",  
                          method="relayout", 
                          args=[{"yaxis.type": "linear"}]),
                     dict(label="Log", 
                          method="relayout", 
                          args=[{"yaxis.type": "log"}])]
                  )]}, height = 700, width = 700,
                  title='Totaal oppervlaktewater gebruik', yaxis_title = "Totaal oppervlaktewater gebruik in miljoen m3")
      # Verdeling maken van aandeel per sector
      fig = px.pie(df_watergebruik, values='Totaal_oppervlaktewater_miljoen_m3', names='Watergebruikers', opacity = 0.7, title='Aandeel totaal oppervlaktewatergebruik per sector')
      fig.update_traces(textinfo='percent+label')
      with st.expander("Zie de Visualisaties"):
        st.plotly_chart(fig2)
        st.plotly_chart(fig)
        st.write("""
          De visualisaties laten zien dat de Energievoorziening, Industrie en de Water- en afval sector veruit het meeste oppervlaktewater gebruiken in Nederland.
          """)
      
    if keuze == 'Zoet oppervlaktewater':
      st.subheader('Zoet oppervlaktewater')
      df_watergebruik['ZoetOppervlaktewater_miljoen_m3'] = np.around(df_watergebruik['ZoetOppervlaktewater_miljoen_m3'], decimals=2)
      with st.expander("Zie het tabel"):
        st.dataframe(df_watergebruik[['Watergebruikers','ZoetOppervlaktewater_miljoen_m3']])

      #Figuur maken van de keuze
      fig2 = px.bar(df_watergebruik, x = 'Jaar', y= 'ZoetOppervlaktewater_miljoen_m3', text_auto=True, color = 'Watergebruikers', opacity = 0.6, barmode='group')
      fig2.update_layout({'updatemenus':[dict(
                 buttons=[
                     dict(label="Linear",  
                          method="relayout", 
                          args=[{"yaxis.type": "linear"}]),
                     dict(label="Log", 
                          method="relayout", 
                          args=[{"yaxis.type": "log"}])]
                  )]}, height = 700, width = 700,
                  title='Totaal zoet oppervlaktewater gebruik', yaxis_title = "Totaal zoet oppervlaktewater gebruik in miljoen m3")
      # Verdeling maken van aandeel per sector
      fig = px.pie(df_watergebruik, values='ZoetOppervlaktewater_miljoen_m3', names='Watergebruikers', opacity = 0.7, title='Aandeel zoet oppervlaktewatergebruik per sector')
      fig.update_traces(textinfo='percent+label')
      with st.expander("Zie de Visualisaties"):
        st.plotly_chart(fig2)
        st.plotly_chart(fig)
        st.write("""
          De visualisaties laten zien dat de Energievoorziening, Industrie en de Water- en afval sector veruit het meeste zoete oppervlaktewater gebruiken in Nederland.
          """)
      
    if keuze == 'Zout oppervlaktewater':
      st.subheader('Zout oppervlaktewater')
      df_watergebruik['ZoutOppervlaktewater_miljoen_m3'] = np.around(df_watergebruik['ZoutOppervlaktewater_miljoen_m3'], decimals=2)
      with st.expander("Zie het tabel"):
        st.dataframe(df_watergebruik[['Watergebruikers','ZoutOppervlaktewater_miljoen_m3']])

      #Figuur maken van de keuze
      fig2 = px.bar(df_watergebruik, x = 'Jaar', y= 'ZoutOppervlaktewater_miljoen_m3', text_auto=True, color = 'Watergebruikers', opacity = 0.6, barmode='group')
      fig2.update_layout({'updatemenus':[dict(
                 buttons=[
                     dict(label="Linear",  
                          method="relayout", 
                          args=[{"yaxis.type": "linear"}]),
                     dict(label="Log", 
                          method="relayout", 
                          args=[{"yaxis.type": "log"}])]
                  )]}, height = 700, width = 700,
                  title='Totaal zout oppervlaktewater gebruik', yaxis_title = "Totaal zout oppervlaktewater gebruik in miljoen m3")
      # Verdeling maken van aandeel per sector
      fig = px.pie(df_watergebruik, values='ZoutOppervlaktewater_miljoen_m3', names='Watergebruikers', opacity = 0.7, title='Aandeel zout oppervlaktewatergebruik per sector')
      fig.update_traces(textinfo='percent+label')
      with st.expander("Zie de Visualisaties"):
        st.plotly_chart(fig2)
        st.plotly_chart(fig)
        st.write("""
          De visualisaties laten zien dat de Energievoorziening en Industrie sector veruit het meeste zoute oppervlaktewater gebruiken in Nederland.
          """)
        
elif pages == 'Verloop van het Watergebruik':
    st.subheader("Verloop van het Watergebruik in Nederland")
    st.markdown("Op deze pagina wordt het verloop van het watergebruik in Nederland weergegeven over de jaren van 2003 tot en met 2020.")
    st.markdown("Om het verloop goed te kunnen weergeven zijn er een aantal lijndiagrammen opgesteld")
    fig_lijn_totaal = go.Figure()
    fig_lijn_totaal.add_trace( go.Scatter(x=list(df_watergebruik_jaar.Jaar), y=list(df_watergebruik_jaar.Totaal_gebruik_miljard_m3)))
    fig_lijn_totaal.update_layout(title_text ="Totaal verloop watergebruik in Nederland",
                          yaxis_title = 'Totaal watergebruik (miljard m3)')
    #Invoegen slider en knoppen
    fig_lijn_totaal.update_layout(xaxis=dict(rangeselector=dict(buttons=list([
                    dict(count=2.5,
                        label="2,5 years",
                        step="year",
                        stepmode="backward"),
                    dict(count=5,
                        label="5 years",
                        step="year",
                        stepmode="backward"),
                    dict(count=7.5,
                        label="7,5 years",
                        step="year",
                        stepmode="backward"),
                    dict(count=10,
                        label="10 years",
                        step="year",
                        stepmode="backward"),
                    dict(step="all")
                ])
            ),
            rangeslider=dict(
                visible=True
            ),
            type="date"
        )
    )
    st.plotly_chart(fig_lijn_totaal)
    st.markdown("In de bovenstaande visualisatie valt op dat er geen grote stijging of daling van het gebruik over de jaren heen is. Het verschil in gebruik ligt nog op hetzelfde niveau")
    # Lijn per soort water (leiding-, grond- of oppervlaktewater)    
    fig_lijn = make_subplots(rows = 3, cols = 1, shared_xaxes = True)
    fig_lijn.add_trace(go.Scatter(x=list(df_watergebruik_jaar.Jaar), y=list(df_watergebruik_jaar.Totaal_leidingwater_miljoen_m3), name = 'Totaal leidingwater(miljoen m3)'),row=1,col =1)
    fig_lijn.add_trace(go.Scatter(x=list(df_watergebruik_jaar.Jaar), y=list(df_watergebruik_jaar.Totaal_grondwater_miljoen_m3), name = 'Totaal grondwater (miljoen m3)'),row=2,col =1)
    fig_lijn.add_trace(go.Scatter(x=list(df_watergebruik_jaar.Jaar), y=list(df_watergebruik_jaar.Totaal_oppervlaktewater_miljoen_m3), name = 'Totaal oppervlaktewater (miljoen m3)'),row=3,col =1)    
    fig_lijn.update_layout(title_text ="Totaal verloop van het gebruik per soort water in Nederland")
    fig_lijn.update_yaxes(title_text="Totaal watergebruik (miljard m3)", row = 2, col = 1)
    st.plotly_chart(fig_lijn)
    with st.expander("Zie het tabel"):
        st.dataframe(df_watergebruik_jaar)
    
    st.markdown("Vanuit het verloop is het goed om de spreiding per sector te weten. Uit de visualisaties komt naar voren dat het oppervlaktewatergebruik de grootste invloed heeft op het totale watergebruik in Nederland. Om het gebruik per sector te achterhalen wordt hieronder eerst de spreiding weergegeven.")
    st.markdown("Met de spreiding wordt de variatie van het gebruik weergegeven van waar tussen de specifieke sector heeft gevarieerd in de jaren 2003 tot en met 2020.")
    # Boxplot
    fig_box = px.box(df_totaal, x = 'Watergebruikers', y ='Totaal_gebruik', color = 'Watergebruikers')
    fig_box.update_layout(
    title = 'Spreiding van het watergebruik per soort sector',
    xaxis_title = 'Watergebruikers',
    yaxis_title = 'Totaal gebruik (miljoen m3)',
    legend_title = 'Watergebruikers'
    )
    fig_box.update_xaxes(categoryorder ='array')
    dropdown_buttons_gebruikers = [  {'label': "Alle gebruikers", 'method': "update",'args': [{"visible": [True, True, True, True, True, True, True, True, True, True, True]}, {'title': 'Alle gebruikers'}]},
                                     {'label': 'Delfstofwinning', 'method': 'update','args': [{'visible': [False, True, False, False, False, False, False, False, False, False, False]}, {'title': 'Spreiding van het totaal watergebruik in de delfstofwinning (miljoen m3)'}]},
                                     {'label': 'Energievoorziening', 'method': 'update','args': [{'visible': [False, False, True, False, False, False, False, False, False, False, False]}, {'title': 'Spreiding van het totaal watergebruik energievoorziening (miljoen m3)'}]},  
                                     {'label': 'Handel', 'method': 'update','args': [{'visible': [False, False, False, True, False, False, False, False, False, False, False]}, {'title': 'Spreiding van het totaal watergebruik handel (miljoen m3)'}]},  
                                     {'label': "Horeca", 'method': "update",'args': [{"visible": [False, False, False, False, True, False, False, False, False, False, False]}, {'title': 'Spreiding van het totaal watergebruik horeca (miljoen m3)'}]},
                                     {'label': 'Huishoudens', 'method': 'update','args': [{'visible': [False, False, False, False, False, True, False, False, False, False, False]}, {'title': 'Spreiding van het totaal watergebruik huishoudens (miljoen m3)'}]},
                                     {'label': "Industrie", 'method': "update",'args': [{"visible": [False, False, False, False, False, False, True, False, False, False, False]}, {'title': 'Spreiding van het totaal watergebruik industrie (miljoen m3)'}]},
                                     {'label': "Landbouw", 'method': "update",'args': [{"visible": [False, False, False, False, False, False, False, True, False, False, False]}, {'title': 'Spreiding van het totaal watergebruik landbouw (miljoen m3)'}]},
                                     {'label': "Vervoer en opslag", 'method': "update",'args': [{"visible": [False, False, False, False, False, False, False, False, True, False, False]}, {'title': 'Spreiding van het totaal watergebruik vervoer en opslag (miljoen m3)'}]},
                                     {'label': "Water- en afvalbedrijven", 'method': "update",'args': [{"visible": [False, False, False, False, False, False, False, False, False, True, False]}, {'title': 'Spreiding van het totaal watergebruik water- en afvalbedrijven(miljoen m3)'}]},
                                     {'label': "Bouw", 'method': "update",'args': [{"visible": [True, False, False, False, False, False, False, False, False, False, False]}, {'title': 'Spreiding van het totaal watergebruik bouw (miljoen m3)'}]}]
    fig_box.update_layout({'updatemenus':[{'type': "dropdown",'x': 1.5,'y': 0.2,'showactive': True,'active': 0,'buttons': dropdown_buttons_gebruikers},
                dict(buttons =[
                     dict(label="Linear",  
                          method="relayout", 
                          args=[{"yaxis.type": "linear"}]),
                     dict(label="Log", 
                          method="relayout", 
                          args=[{"yaxis.type": "log"}]),
                                  ])]})
    st.plotly_chart(fig_box)
    with st.expander("Filter gekozen sector om alle gebruiken te zien"):
        st.markdown("In de onderstaande balk kunt u een van de watergebruikers invullen.")
        st.markdown("De sectoren waarvan het gebruik bekend is zijn: Landbouw, Huishoudens, Delfstofwinning, Industrie, Energievoorziening, Water- en afvalbedrijven, Bouw, Handel, Vervoer en opslag, Horeca.")
        input = st.text_input('Geef een watergebruiker op','Bijvoorbeeld: Horeca', max_chars=25)
        message_annotation = {
          'x': 0.5, 'y':1.1, 'xref': 'paper', 'yref': 'paper',
          'text': f'Totaal watergebruik in de {input} (miljard m3)',
          'font': {'size': 18, 'color': 'Black'},
          'bgcolor': 'rgb(210, 210, 210)', 'showarrow': False}
        df_totaal1 = df_totaal.loc[df_totaal['Watergebruikers'] == input]
        df_totaal1 = df_totaal1.reset_index(drop= True)
        st.dataframe(df_totaal1)
        fig_lijn_totaal_sector = go.Figure()
        fig_lijn_totaal_sector.add_trace( go.Scatter(x=list(df_totaal1.Jaar), y=list(df_totaal1.Totaal_gebruik)))
        fig_lijn_totaal_sector.update_layout( {'annotations':[message_annotation]}, yaxis_title = 'Totaal watergebruik in de sector (miljoen m3)')
        #Invoegen slider en knoppen
        fig_lijn_totaal_sector.update_layout(xaxis=dict(rangeslider=dict(visible=True),type="date"))
        st.plotly_chart(fig_lijn_totaal_sector)
elif pages == 'Toekomstig watergebruik':
  st.subheader("Het toekomstige watergebruik in Nederland")
  st.markdown("Op deze pagina wordt een voorspelling gedaan van het watergebruik in Nederland in de toekomst.")
  st.markdown("Om het verloop goed te kunnen weergeven zijn er een aantal lijndiagrammen opgesteld")
  st.markdown('Waterbedrijf Vitens heeft de verwachting dat het totale watergebruik per jaar zal toenemen met 1.25%')
  with st.expander("Zie tabel"):
    st.dataframe(df_model)
  st.plotly_chart(fig_model)
  
