import streamlit as st
from manu import Manu
import pandas as pd

# funções
ms = Manu()

st.title('Manu')

# descrição
txt_descricao = 'De uma tabela com quatro colunas, obtenha *insights* incríveis de manutenção! ⚙️❇️\n'
st.write(txt_descricao)

tab_indicador, tab_registro = st.tabs(['Indicadores', 'Registros'])

with tab_indicador:
    # periodo padrão de analise
    data_inicio_dados = ms.get_dados_processados()['Abertura'].min()
    data_fim_dados = ms.get_dados_processados()['Encerramento'].max() + pd.Timedelta(days=1)
    data_analise = st.date_input('Período de análise', (data_inicio_dados, data_fim_dados))
    # converte para o formato data do pandas
    data_inicio = pd.to_datetime(data_analise[0])
    data_fim = pd.to_datetime(data_analise[1])
    # indicadores de acordo com as data de inicio e fim
    df_indicadores = ms.indicadores(data_inicio, data_fim)
    
    # indicadores da planta
    st.caption('Métricas do conjunto de equipamentos')
    mttr_media = round(df_indicadores['MTTR'].mean(), 2)
    mtbf_media = round(df_indicadores['MTBF'].mean(), 2)
    disponibilidade_media = round(df_indicadores['Disponibilidade'].mean(), 2)
    total_numero_paradas = df_indicadores['Número Paradas'].sum()
    
    col_mttr, col_mtbf, col_disponibilidade, col_numero_paradas = st.columns(4)
    col_mttr.metric('MTTR [h]', mttr_media)
    col_mtbf.metric('MTBF [h]', mtbf_media)
    col_disponibilidade.metric('Disponibilidade', disponibilidade_media)
    col_numero_paradas.metric('Número Paradas', total_numero_paradas)
    
    # dataframe com os dados
    st.caption('Dados por equipamento')
    st.dataframe(df_indicadores, use_container_width=True)

with tab_registro:
    with st.form("registro"):
        ms = Manu()
        dados = ms.get_dados()
        st.dataframe(dados, use_container_width=True)
        # input de texto para execução das funções
        query = st.text_input('Função')
        
        atualizar = st.form_submit_button("Executar")
        if atualizar:
            try:
                res = ms.alterar_tabela(query)
                dados = ms.get_dados()
                st.experimental_rerun()
            except Exception as e:
                st.error(e)