import streamlit as st
import numpy as np
import pandas as pd
import altair as alt
import requests

# Page setup
st.set_page_config(page_title='IPMA Weather Alerts')
st.title('Weather Alerts Explorer')

with st.expander('Sobre esta app'):
  st.markdown('**O que esta app consegue fazer?**')
  st.info('Esta app permite ver os Avisos Meteorológicos através da API do IPMA - https://api.ipma.pt/ - , com previsão até 3 dias.')
  st.markdown('**Como utilizar esta app?**')
  st.warning('Deverá seleccionar o Aviso Meteorológico que pretende consultar, e automaticamente será elaborado o gráfico de Aviso e Tendência.')
  st.markdown('**Formulário**')
  st.warning('Poderá utilizar o formulário para adicionar condições meteorológicas na sua área de residência e respetivas observações, em tempo real.')
  st.markdown('**Elaboração da app**')
  st.warning('A aplicação foi desenvolvida por Pedro Gomes e Tiago Cardoso, da Secretaria Geral do Ambiente, utilizando o assistente virtual Cody na elaboração, debugging e simplificação do código, e a API do IPMA numa lógica de utilização de dados abertos de fontes oficiais.')
  
# API data load
url = 'https://api.ipma.pt/open-data/forecast/warnings/warnings_www.json'
response = requests.get(url)
data = response.json()

df = pd.DataFrame(data)

# Widgets
awareness_types = st.multiselect('Awareness Types', df['awarenessTypeName'].unique())
awareness_levels = st.multiselect('Awareness Levels', df['awarenessLevelID'].unique())

# Filter data
df_filtered = df[df['awarenessTypeName'].isin(awareness_types) &
                df['awarenessLevelID'].isin(awareness_levels)]

# Display dataframe 
st.dataframe(df_filtered)

# Create chart data
chart_data = df_filtered.groupby(['awarenessTypeName','startTime']).count().reset_index() 

# Display chart
chart = alt.Chart(chart_data).mark_area().encode(
    x='startTime',
    y='idAreaAviso',
    color='awarenessTypeName'
)

# Time series chart
time_chart = alt.Chart(df.groupby('startTime').count().reset_index()).mark_line().encode(
    x='startTime',
    y='idAreaAviso'
)

# Pie chart   
pie_chart = alt.Chart(df['awarenessLevelID'].value_counts().reset_index()).mark_arc().encode(
    theta=alt.Theta(field='idAreaAviso', type='quantitative'),
    color='awarenessLevelID:N'
)

# Create subplots
charts = alt.vconcat(
    time_chart.properties(title='Alerts Over Time'),
    pie_chart.properties(title='Alerts by Level')
).configure_view(
    strokeWidth=0
)

st.markdown("## Tipologia de Aviso")
st.altair_chart(chart)

st.markdown("## Total de Avisos Meteorológicos")
st.altair_chart(time_chart)

# Create empty dataframe
weather_df = pd.DataFrame(columns=['Hora', 'Local', 'Observações', 'Ocorrência']) 

# Form
with st.form('weather_form'):

    st.header('Formulário de Observações')

    Hora = st.text_input('Hora')
    Local = st.text_input('Local')
    Observações = st.text_input('Observações')
    Ocorrência = st.selectbox('Ocorrência', ['Neve', 'Agitação Marítima', 'Nevoeiro', 'Tempo Quente', 'Tempo Frio', 'Precipitação', 'Trovoada', 'Vento'])
    
    submitted = st.form_submit_button('Submit')
    
# On form submit    
if submitted:

    # Append data to dataframe 
    weather_df = weather_df.append({
        'Hora': Hora,
        'Local': Local,
        'Observações': Observações,
        'Ocorrência': Ocorrência
    }, ignore_index=True)
    
    # Success message
    st.success('Submitted')

# Display dataframe
st.dataframe(weather_df)
