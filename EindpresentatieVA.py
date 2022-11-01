#!/usr/bin/env python
# coding: utf-8

# # Casus Eindopdracht Visual Analytics- Giel, Roy 

# ## Minor Data Science
# ### Studenten: Giel Suweijn (500835117) en Roy Pontman (500826482)

# ## Inladen Packages

# In[2]:


import pandas as pd
import geopandas as gpd
import numpy as np
import requests
import plotly.express as px
import plotly.figure_factory as ff
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
df_leidingwater = pd.read_csv('Leidingwater.csv', sep =';')
df_grondwater = pd.read_csv('Grondwater.csv', sep =';')
df_oppervlaktewater = pd.read_csv('Oppervlaktewater.csv', sep =';')

# ## Bewerken van de Data
# ###Bewerken data watergebruik

# Voor grondwater en oppervlaktewater zijn er NAN-values omdat het hier gaat om huishoudelijke watergebruikers
# of gebruikers die alleen gebruik maken van leidingwater (zoals bijvoorbeeld ook Horeca). Hierdoor vullen we alle NAN-values met 0
df_grondwater = df_grondwater.fillna(0)
df_oppervlaktewater = df_oppervlaktewater.fillna(0)

df_watergebruik = df_leidingwater.merge(df_grondwater, on = ['ID','Perioden','Watergebruikers']) \
                    .merge(df_oppervlaktewater, on = ['ID','Perioden','Watergebruikers'])
df_watergebruik['Jaar'] = df_watergebruik['Perioden'].str[:4]
df_watergebruik.drop(['Perioden','ID'],axis=1, inplace=True)
df_watergebruik['Watergebruikers'] = df_watergebruik['Watergebruikers'].astype(str)
# Alle sectoren zijn gecodeerd in de download van de CSV, hierdoor moeten ze allemaal weer de goede naam krijgen.
for i,column in df_watergebruik.iterrows():
    if column['Watergebruikers'] == '301000':
        df_watergebruik.loc[i, 'Watergebruikers'] = 'Landbouw'
    if column['Watergebruikers'] == '1050010':
        df_watergebruik.loc[i, 'Watergebruikers'] = 'Huishoudens'
    if column['Watergebruikers'] == '305700':
        df_watergebruik.loc[i, 'Watergebruikers'] = 'Delfstofwinning'
    if column['Watergebruikers'] == '307500':
        df_watergebruik.loc[i, 'Watergebruikers'] = 'Industrie'
    if column['Watergebruikers'] == '307600':
        df_watergebruik.loc[i, 'Watergebruikers'] = 'Voedselwinning'
    if column['Watergebruikers'] == '346600':
        df_watergebruik.loc[i, 'Watergebruikers'] = 'Energievoorziening'
    if column['Watergebruikers'] == '348000':
        df_watergebruik.loc[i, 'Watergebruikers'] = 'Water- en afvalbedrijven'
    if column['Watergebruikers'] == '383100':
        df_watergebruik.loc[i, 'Watergebruikers'] = 'Vervoer en opslag'
    if column['Watergebruikers'] == '389100':
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

# ###Bewerken data bodemgebruik

# ## Streamlit Code

# In[ ]:


pages = st.sidebar.selectbox('Pagina' ,('Home','Bodemgebruik','Watergebruik', 'Ritteninformatie datasets'))

if pages == 'Home':
    st.title("**Bodem- en watergebruik in Nederland**")
    st.markdown("Met dit dashboard wordt geprobeerd een zo een compleet mogelijk beeld te weergeven van de ontwikkeling van de energievraag van logistieke bedrijven en de knelpunten in het netwerk. Omdat er al een tekort is aan capaciteit op het elektriciteitsnetwerk, is de verwachting dat de aanleg van nieuwe aansluitingen door de netbeheerder tot wel 8 jaar kan duren. Daarom is het belangrijk om nu alvast in kaart te brengen wat de verwachtte energievraag is (hoeveel, waar en wanneer) in de toekomstige situatie zodat we ons op tijd kunnen voorbereiden en logistieke vervoerders niet hoeven te wachten met het aanschaffen van elektrische voertuigen omdat er onvoldoende netwerkcapaciteit beschikbaar is. Dat zou de energietransitie onnodig remmen.")

    #st.markdown("Welkom op het dashboard van groep 22. Gebruik de knoppen in de sidebar om tussen de verschillende paginas te navigeren. ")


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
    number = st.number_input('Voer een jaar in', min_value=2003, max_value=2020, value=2003, step=1)
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
                  )]}, height = 700, width = 1000,
                  title='Totaal watergebruik voor Leidingwater', yaxis_title = "Leidingwater gebruik in miljoen m3")
      
      # Verdeling maken van aandeel per sector
      fig = px.pie(df_watergebruik, values='Totaal_leidingwater_miljoen_m3', names='Watergebruikers', title='Aandeel watergebruik per sector')
        with st.expander("See Visualizations"):
          st.plotly_chart(fig2)
          st.plotly_chart(fig)
          st.write("""
            De grafieken laten zien dat huishoudens en horeca veruit het meeste leidingwater gebruiken in Nederland.
            """)   

      
      
    if keuze == 'Drinkwater':
      st.subheader('Drinkwater')
      df_watergebruik['Drinkwater_miljoen_m3'] = np.around(df_watergebruik['Drinkwater_miljoen_m3'], decimals=2)
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
                  )]}, height = 700, width = 1000,
                  title='Totaal watergebruik voor Drinkwater', yaxis_title = "Drinkwater gebruik in miljoen m3")
      
      
    if keuze == 'Industriewater':
      st.subheader('Industriewater')
      df_watergebruik['industriewater_miljoen_m3'] = np.around(df_watergebruik['industriewater_miljoen_m3'].tolist(), decimals=2)
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
                  )]}, height = 700, width = 1000,
                  title='Totaal watergebruik voor Industriewater', yaxis_title = "Industriewater gebruik in miljoen m3")
      st.plotly_chart(fig2)
      
    if keuze == 'Totaal grondwater':
      st.subheader('Totaal grondwater')
      df_watergebruik['Totaal_grondwater_miljoen_m3'] = np.around(df_watergebruik['Totaal_grondwater_miljoen_m3'], decimals=2)
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
                  )]}, height = 700, width = 1000,
                  title='Totaal watergebruik voor Grondwater', yaxis_title = "Grondwater gebruik in miljoen m3")
      st.plotly_chart(fig2)
      
    if keuze == 'Koelingwater':
      st.subheader('Koelingwater')
      df_watergebruik['Koelingwater_miljoen_m3'] = np.around(df_watergebruik['Koelingwater_miljoen_m3'], decimals=2)
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
                  )]}, height = 700, width = 1000,
                  title='Totaal watergebruik voor Koelwater', yaxis_title = "Koelwater gebruik in miljoen m3")
      st.plotly_chart(fig2)
      
    if keuze == 'Overige gebruik grondwater':
      st.subheader('Overige gebruik grondwater')
      df_watergebruik['OverigeGebruikGrondwater_miljoen_m3'] = np.around(df_watergebruik['OverigeGebruikGrondwater_miljoen_m3'], decimals=2)
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
                  )]}, height = 700, width = 1000,
                  title='Totaal grondwatergebruik voor overige doeleinde', yaxis_title = "Overige gebruik grondwater in miljoen m3")
      st.plotly_chart(fig2)
      
    if keuze == 'Totaal oppervlaktewater':
      st.subheader('Totaal oppervlaktewater')
      df_watergebruik['Totaal_oppervlaktewater_miljoen_m3'] = np.around(df_watergebruik['Totaal_oppervlaktewater_miljoen_m3'], decimals=2)
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
                  )]}, height = 700, width = 1000,
                  title='Totaal oppervlaktewater gebruik', yaxis_title = "Totaal oppervlaktewater gebruik in miljoen m3")
      st.plotly_chart(fig2) 
      
    if keuze == 'Zoet oppervlaktewater':
      st.subheader('Zoet oppervlaktewater')
      df_watergebruik['ZoetOppervlaktewater_miljoen_m3'] = np.around(df_watergebruik['ZoetOppervlaktewater_miljoen_m3'], decimals=2)
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
                  )]}, height = 700, width = 1000,
                  title='Totaal zoet oppervlaktewater gebruik', yaxis_title = "Totaal zoet oppervlaktewater gebruik in miljoen m3")
      st.plotly_chart(fig2) 
      
    if keuze == 'Zout oppervlaktewater':
      st.subheader('Zout oppervlaktewater')
      df_watergebruik['ZoutOppervlaktewater_miljoen_m3'] = np.around(df_watergebruik['ZoutOppervlaktewater_miljoen_m3'], decimals=2)
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
                  )]}, height = 700, width = 1000,
                  title='Totaal zout oppervlaktewater gebruik', yaxis_title = "Totaal zout oppervlaktewater gebruik in miljoen m3")
      st.plotly_chart(fig2)         
elif pages == 'Ritteninformatie datasets':
    
    
    
    st.subheader("Informatie over ritten")
    st.markdown("Voor enkele transporteurs is hieronder een schatting van wat de energievraag zou zijn in het geval van dat de ritten door een elektrische vrachtwagen zou worden uitgevoerd. Hierbij gaan we de vraag beantwoorden hoeveel elektriciteit er nodig zou zijn om de rit uit te voeren, en of dit op een bedrijventerrein kan worden gedaan of langs de snelweg.")
    
    voertuig_ids_string = np.array2string((np.sort(AlleVoertuigen_merged_df['voertuig_id'].unique())), separator=',')
    voertuig_ids_string = re.sub(r'[\[\]]', r'', voertuig_ids_string)

    voertuig_ids_december = np.array2string((np.sort(december_merged_df['voertuig_id'].unique())), separator=',')
    voertuig_ids_december = re.sub(r'[\[\]]', r'', voertuig_ids_december)
    
    st.markdown("Voorbeelden van ID's in Allevoertuigen: " + voertuig_ids_string)
    st.markdown("Voorbeelden van ID's in December: " + voertuig_ids_december)

    number_2 = st.number_input('Voeg een voertuig ID in', min_value=1, max_value=200, value=3, step=1)
     
    dataset = st.selectbox('Datasets', ('December', 'Allevoertuigen'))
    scenario = st.selectbox( 'Scenario', ('**Scenario 1:** Alle voertuigen Elektrisch',"**Scenario 2:** Grotere accu's",'**Scenario 3:** Vergroot vermogen van de laders', '**Scenario 4:** brandstofkosten vergelijken'))
    if dataset == 'Allevoertuigen':
        merged_df_voertuig = AlleVoertuigen_merged_df.loc[AlleVoertuigen_merged_df['voertuig_id'] == number_2]

        merged_df_voertuig.reset_index(drop=True, inplace=True)
        if merged_df_voertuig['Voertuig'][0] == 'Bestelbus':
            simulatie_bestelbus_allevoertuigen_input = simulate(merged_df_voertuig,
                          zuinig = 0.2, 
                          aansluittijd = 600, 
                          battery = 60, 
                          laadvermogen_bedrijfsterrein = 22, 
                          laadvermogen_snelweg = 80)
            simulatie_dataframe_allevoertuigen  = simulatie_bestelbus_allevoertuigen_input

        if merged_df_voertuig['Voertuig'][0] == 'Vrachtwagen':
            simulatie_vrachtwagen_allevoertuigen_input = simulate(merged_df_voertuig,
                          zuinig = 1, 
                          aansluittijd = 600,
                          battery = 300,
                          laadvermogen_bedrijfsterrein = 43,
                          laadvermogen_snelweg = 150)
            simulatie_dataframe_allevoertuigen  = simulatie_bestelbus_allevoertuigen_input
        
        if scenario == '**Scenario 1:** Alle voertuigen Elektrisch':
            st.markdown("**Scenario 1:** Alle EV's Elektrisch")
            st.dataframe(simulatie_vrachtwagen_allevoertuigen)
            #st.plotly_chart(fig_euro_Dec)
            #st.plotly_chart(fig_bijladen)
            #st.plotly_chart(fig_stop)
        elif scenario == "**Scenario 2:** Grotere accu's":
            st.markdown("**Scenario 2:** Grotere accu's")
            st.markdown("Dubbel vermogen op de batterij betekent dat er weinig tot nooit meer moet worden geladen op de snelweg")
            st.markdown("Enkel batterijvermogen Dataframe")
            st.dataframe(simulatie_dataframe_allevoertuigens[['Afstand', 'energie_beginstand', 'bijladen_bedrijfsterrein', 'laadplek', 'laadtijd', 'totale_kosten_bijladen(Euro)']])
            st.markdown("Dubbel batterijvermogen Dataframe")
            st.dataframe(allevoertuigen_dubbel_batterij[['Afstand','energie_beginstand', 'bijladen_bedrijfsterrein', 'laadplek', 'laadtijd', 'totale_kosten_bijladen(Euro)']])
            #st.plotly_chart(fig_energie_dubbel_batterij)
            #st.plotly_chart(fig_energie_dubbel_vermogen)
        elif scenario == "**Scenario 3:** Vergroot vermogen van de laders":
            st.markdown("**Scenario 3:** Vergroot vermogen van de laders")
            st.markdown("Snelweglaadvermogen op het bedrijfsterrein betekent dat er in de nacht sneller geladen kan worden. De laadtijd op het bedrijfsterrein is bijna 4 keer zo snel. Daarnaast kan, als de bezoektijd lang genoeg is, vaak sneller en meer geladen worden als het laadvermogen op het bedrijfsterrein net zo snel is als op de snelweg")
            st.markdown("Gecombineerd oplaadvermogen Dataframe")
            st.dataframe(simulatie_allevoertuigen_laadtijd_cleaned)
            #st.plotly_chart(fig_energie_dubbel_vermogen)
            #st.plotly_chart(fig_energie_dubbel_vermogen_Dec)
        elif scenario == "**Scenario 4:** brandstofkosten vergelijken":
            st.dataframe(df_totale_kosten_plus_waterstof)
            st.markdown("**Scenario 4:** brandstofkosten vergelijken")
            st.markdown("Groot verschil tussen alle brandstoffen")
            #st.plotly_chart(fig_kosten)
    if dataset == 'December':
        merged_df_december = december_merged_df.loc[december_merged_df['voertuig_id'] == number_2]
        merged_df_december.reset_index(drop=True, inplace=True)

        if merged_df_december['Voertuig'][0] == 'Bestelbus':
            simulatie_bestelbus_december_input = simulate(merged_df_december,
                          zuinig = 0.2, 
                          aansluittijd = 600, 
                          battery = 60, 
                          laadvermogen_bedrijfsterrein = 22, 
                          laadvermogen_snelweg = 80)
            simulatie_dataframe_december = simulatie_bestelbus_december_input

        if merged_df_december['Voertuig'][0] == 'Vrachtwagen':
            simulatie_vrachtwagen_december_input = simulate(merged_df_december,
                          zuinig = 1, 
                          aansluittijd = 600,
                          battery = 300,
                          laadvermogen_bedrijfsterrein = 43,
                          laadvermogen_snelweg = 150)
            simulatie_dataframe_december = simulatie_vrachtwagen_december_input
            
        if scenario == '**Scenario 1:** Alle voertuigen Elektrisch':
            st.markdown("**Scenario 1:** Alle EV's Elektrisch")
            st.dataframe(simulatie_vrachtwagen_allevoertuigen)
            #st.plotly_chart(fig_euro_Dec)
            #st.plotly_chart(fig_bijladen)
            #st.plotly_chart(fig_stop)
        elif scenario == "**Scenario 2:** Grotere accu's":
            st.markdown("**Scenario 2:** Grotere accu's")
            st.markdown("Dubbel vermogen op de batterij betekent dat er weinig tot nooit meer moet worden geladen op de snelweg")
            st.markdown("Enkel batterijvermogen Dataframe")
            st.dataframe(simulatie_dataframe_december[['Afstand', 'energie_beginstand', 'bijladen_bedrijfsterrein', 'laadplek', 'laadtijd', 'totale_kosten_bijladen(Euro)']])
            st.markdown("Dubbel batterijvermogen Dataframe")
            st.dataframe(december_dubbel_batterij[['Afstand', 'energie_beginstand', 'bijladen_bedrijfsterrein', 'laadplek', 'laadtijd', 'totale_kosten_bijladen(Euro)']])
            #st.plotly_chart(fig_energie_dubbel_batterij)
            #st.plotly_chart(fig_energie_dubbel_vermogen)
        elif scenario == "**Scenario 3:** Vergroot vermogen van de laders":
            st.markdown("**Scenario 3:** Vergroot vermogen van de laders")
            st.markdown("Snelweglaadvermogen op het bedrijfsterrein betekent dat er in de nacht sneller geladen kan worden. De laadtijd op het bedrijfsterrein is bijna 4 keer zo snel. Daarnaast kan, als de bezoektijd lang genoeg is, vaak sneller en meer geladen worden als het laadvermogen op het bedrijfsterrein net zo snel is als op de snelweg")
            st.dataframe(simulatie_december_laadtijd_cleaned)
            #st.plotly_chart(fig_energie_dubbel_vermogen)
            #st.plotly_chart(fig_energie_dubbel_vermogen_Dec)
        elif scenario == "**Scenario 4:** brandstofkosten vergelijken":
            st.markdown("**Scenario 4:** brandstofkosten vergelijken")
            st.markdown("Groot verschil tussen alle brandstoffen")
            st.dataframe(df_totale_kosten_plus_waterstof)

