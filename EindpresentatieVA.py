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
from shapely.geometry import Point
import missingno as msno
import statsmodels.api as sm
#!pip install streamlit
import streamlit as st
from fuzzywuzzy import fuzz
import folium


# ## Ophalen Datasets

# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# ## Streamlit Code

# In[ ]:


pages = st.sidebar.selectbox('Pagina' ,('Home','Terrein Kaart','Verbruik', 'Ritteninformatie datasets'))

if pages == 'Home':
    st.header("**Klimaatneutraal rijden**")
    st.markdown("Met dit dashboard wordt geprobeerd een zo een compleet mogelijk beeld te weergeven van de ontwikkeling van de energievraag van logistieke bedrijven en de knelpunten in het netwerk. Omdat er al een tekort is aan capaciteit op het elektriciteitsnetwerk, is de verwachting dat de aanleg van nieuwe aansluitingen door de netbeheerder tot wel 8 jaar kan duren. Daarom is het belangrijk om nu alvast in kaart te brengen wat de verwachtte energievraag is (hoeveel, waar en wanneer) in de toekomstige situatie zodat we ons op tijd kunnen voorbereiden en logistieke vervoerders niet hoeven te wachten met het aanschaffen van elektrische voertuigen omdat er onvoldoende netwerkcapaciteit beschikbaar is. Dat zou de energietransitie onnodig remmen.")

    #st.markdown("Welkom op het dashboard van groep 22. Gebruik de knoppen in de sidebar om tussen de verschillende paginas te navigeren. ")


elif pages == 'Terrein Kaart':
    st.subheader('Kaarten Bedrijventerreinen')
    st.markdown("In de kaart zijn de energiebehoeftes van Schiphol tradepark en WFO per gebouw weergegeven. Hiermee gaan we een geschatte energievraag analyseren van op basis van voertuigregistraties. Op basis van publieke data en deelse CBS data. Wordt een inschatting gemaakt hoe de energiebehoefte/voorraad op bedrijventerreinen.")
    folium_static(mwfo)#Kaart1
    folium_static(mstp)#Kaart2
elif pages == 'Verbruik':
    st.subheader('Energie verbruik per dag')
    st.markdown('In onderstaande velden voer een voertuig ID in om het energieverbruik over een dag van een vrachtwagen te visualiseren.')
    number = st.number_input('Voeg een voertuig ID in', min_value=1, max_value=200, value=1, step=1)

        #Knoppen maken zodat een dag van het jaar gekozen kan worden
    datum_2022 = st.date_input("Kies hier een datum voor het energieprofiel van 2022", datetime.date(2021, 4, 1),
                      min_value = datetime.date(2021, 4, 1), max_value = datetime.date(2021, 4, 30))



    

    merged_df_voertuig = AlleVoertuigen_merged_df.loc[AlleVoertuigen_merged_df['voertuig_id'] == number]

    merged_df_voertuig.reset_index(drop=True, inplace=True)
    if merged_df_voertuig['Voertuig'][0] == 'Bestelbus':
        simulatie_bestelbus_allevoertuigen_input = simulate(merged_df_voertuig,
                      zuinig = 0.2, 
                      aansluittijd = 600, 
                      battery = 60, 
                      laadvermogen_bedrijfsterrein = 22, 
                      laadvermogen_snelweg = 80)
        simulatie_auto_datum_test =simulatie_bestelbus_allevoertuigen_input[simulatie_bestelbus_allevoertuigen_input['Begindatum'].dt.date == datum_2022]

    if merged_df_voertuig['Voertuig'][0] == 'Vrachtwagen':
        simulatie_vrachtwagen_allevoertuigen_input = simulate(merged_df_voertuig,
                      zuinig = 1, 
                      aansluittijd = 600,
                      battery = 300,
                      laadvermogen_bedrijfsterrein = 43,
                      laadvermogen_snelweg = 150)
        simulatie_auto_datum_test = simulatie_vrachtwagen_allevoertuigen_input[simulatie_vrachtwagen_allevoertuigen_input['Begindatum'].dt.date == datum_2022]



    simulatie_auto_datum_test.reset_index(inplace=True, drop=True)

    fig1 = px.line(simulatie_auto_datum_test ,x='Begintijd', y='energie_beginstand', color=px.Constant(datum_2022),
             labels=dict(x=datum_2022, y="kWh", color="Time Period"))
    st.plotly_chart(fig1)
    st.plotly_chart(fig_energie)
    st.plotly_chart(fig_euro) 
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

