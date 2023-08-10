import streamlit as st
import pandas as pd
import plotly.express as px
import colorcet as cc


@st.cache_data
def get_siglas():
    df = pd.read_csv('.\\sigla.csv')
    df = df.rename(columns={'Sigla': 'tempo'})
    df = df.set_index('tempo')
    return df


@st.cache_data
def get_coord():
    df = pd.read_csv('https://raw.githubusercontent.com/kelvins/Municipios-Brasileiros/main/csv/municipios.csv')
    est = pd.read_csv('https://raw.githubusercontent.com/kelvins/Municipios-Brasileiros/main/csv/estados.csv')
    est = est.set_index('codigo_uf')
    df = df.join(est, 'codigo_uf', rsuffix='_est')
    df['id'] = df['nome'] + '-' + df['uf']
    df['color'] = (cc.glasbey * 23)[:len(df)]
    return df


def get_previsao(id):
    siglas = get_siglas()
    df = pd.DataFrame()
    for i in id.index:
        lat = id.at[i, 'latitude']
        long = id.at[i, 'longitude']
        dfi = pd.concat([pd.read_xml(f'http://servicos.cptec.inpe.br/XML/cidade/7dias/{lat}/{long}/previsaoLatLon.xml', encoding='cp1252'),
                         pd.read_xml(f'http://servicos.cptec.inpe.br/XML/cidade/{lat}/{long}/estendidaLatLon.xml', encoding='cp1252')
                         ])
        dfi['cidade'] = id.at[i, 'nome']
        df = pd.concat([df, dfi])
    df = df.join(siglas, 'tempo')
    df = df.dropna(subset=['dia'])
    df = df.drop(columns=['tempo', 'uf', 'atualizacao', 'nome'])
    return df


st.set_page_config(layout='wide')
st.title('Previsão do tempo e Localização')
df = get_coord()
cols = st.columns(2)
cidades = cols[0].multiselect('Cidades', df['id'])
dados = df[df['id'].isin(cidades)]
if not dados.empty:
    cols[1].dataframe(dados[['nome', 'nome_est', 'regiao', 'ddd', 'latitude', 'longitude']], hide_index=True, width=500)
    prev = get_previsao(dados)
    cols[0].plotly_chart(px.line(prev, 'dia', ['maxima', 'minima'], color='cidade', color_discrete_sequence=dados['color'].tolist(), hover_data=['iuv', 'Descrição']))
    cols[0].write('dados: CPTEC/INPE')
    cols[1].map(dados.reset_index(), zoom=3, color='color')
