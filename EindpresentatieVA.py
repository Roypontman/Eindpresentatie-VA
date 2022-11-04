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
import statsmodels.api as sm
#!pip install streamlit
import streamlit as st
from fuzzywuzzy import fuzz
import datetime
from datetime import date
#import folium


# ## Ophalen Datasets
#df_leidingwater = pd.read_csv('Leidingwater.csv', sep =';')
#df_grondwater = pd.read_csv('Grondwater.csv', sep =';')
#df_oppervlaktewater = pd.read_csv('Oppervlaktewater.csv', sep =';')

# ## Bewerken van de Data
# ###Bewerken data watergebruik

# Voor grondwater en oppervlaktewater zijn er NAN-values omdat het hier gaat om huishoudelijke watergebruikers
# of gebruikers die alleen gebruik maken van leidingwater (zoals bijvoorbeeld ook Horeca). Hierdoor vullen we alle NAN-values met 0
#df_grondwater = df_grondwater.fillna(0)
#df_oppervlaktewater = df_oppervlaktewater.fillna(0)

#df_watergebruik = df_leidingwater.merge(df_grondwater, on = ['ID','Perioden','Watergebruikers']) \
#                   .merge(df_oppervlaktewater, on = ['ID','Perioden','Watergebruikers'])
# ## Ophalen Dataset door middel van API
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
df_watergebruik['Totaal_gebruik'] = df_watergebruik['Totaal_leidingwater_miljoen_m3'] + df_watergebruik['Totaal_grondwater_miljoen_m3'] + df_watergebruik['Totaal_oppervlaktewater_miljoen_m3']
df_watergebruik_jaar = df_watergebruik.groupby(['Jaar'])['Totaal_leidingwater_miljoen_m3','Totaal_grondwater_miljoen_m3', 'Totaal_oppervlaktewater_miljoen_m3','Totaal_gebruik'].sum()
df_watergebruik_jaar['Totaal_gebruik_miljard_m3'] = df_watergebruik_jaar['Totaal_gebruik']/1000
df_totaal = df_watergebruik.groupby(['Jaar','Watergebruikers'])['Totaal_leidingwater_miljoen_m3','Totaal_grondwater_miljoen_m3','Totaal_oppervlaktewater_miljoen_m3'].sum()
#df_totaal[['Totaal_leidingwater_miljoen_m3','Totaal_grondwater_miljoen_m3','Totaal_oppervlaktewater_miljoen_m3']] = df_totaal[['Totaal_leidingwater_miljoen_m3','Totaal_grondwater_miljoen_m3','Totaal_oppervlaktewater_miljoen_m3']]/1000
df_totaal['Totaal_gebruik'] = df_totaal['Totaal_leidingwater_miljoen_m3'] + df_totaal['Totaal_grondwater_miljoen_m3'] + df_totaal['Totaal_oppervlaktewater_miljoen_m3']
df_totaal['Totaal_gebruik_miljard_m3'] = df_totaal['Totaal_gebruik']/1000
df_watergebruik_jaar = df_watergebruik_jaar.reset_index()
df_totaal = df_totaal.reset_index()




# ###Bewerken data bodemgebruik

# ## Streamlit Code

# ### Achtergrond invoegen
def add_bg_from_url():
    st.markdown(
         f"""
         <style>
         .stApp {{
             background-image: Achtergrond.png;
             background-attachment: fixed;
             background-size: cover;
             #opacity: 0.55
         }}
         </style>
         """,
         unsafe_allow_html=True
     )

add_bg_from_url() 

pages = st.sidebar.selectbox('Pagina' ,('Home','Bodemgebruik','Watergebruik', 'Verloop van het Watergebruik', 'Toekomstig watergebruik'))
st.sidebar.markdown('**Gemaakt door**: Giel Suweijn en Roy Pontman',unsafe_allow_html=True)
st.sidebar.markdown('              Minor Data Science')
if pages == 'Home':
    st.title("**Bodem- en watergebruik in Nederland**")
    st.markdown("Met dit dashboard wordt geprobeerd het bodem- en watergerbuik in Nederland in kaart te krijgen. Door middel van datasets van CBS zijn jaargebruiken opgehaald en geanalyseerd. In de linker ribbon kunt u zich bewegen door het dashboard door middel van een dropdown. In deze dropdown is er een keuze te maken tussen het bodemgebruik, het watergebruik, het verloop van het watergebruik en het toekomstige watergebruik.")
    image = Image.open('Water.jpg')
    st.image(image, caption='De basis is water',width = 600)
    image = Image.open('Bodem.jpg')
    st.image(image, caption='Complexe indeling in Nederland',width =600)
    


elif pages == 'Bodemgebruik':
    st.subheader('Kaarten Bedrijventerreinen')
    st.markdown("In de kaart zijn de energiebehoeftes van Schiphol tradepark en WFO per gebouw weergegeven. Hiermee gaan we een geschatte energievraag analyseren van op basis van voertuigregistraties. Op basis van publieke data en deelse CBS data. Wordt een inschatting gemaakt hoe de energiebehoefte/voorraad op bedrijventerreinen.")
    folium_static(mwfo)#Kaart1
    folium_static(mstp)#Kaart2


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
          De visualisaties laten zien dat de Industrie de enige sector is die industriewater gebruikt in Nederland. Dit komt door een fout in de dataset, waardoor meerdere sectoren vallen onder Industrie. Hiermee valt alles onder één sector.
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
  
