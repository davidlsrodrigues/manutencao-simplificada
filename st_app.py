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
    data_inicio_dados = ms.get_dados_processados()['Data Abertura'].min()
    data_fim_dados = ms.get_dados_processados()['Data Abertura'].max() + pd.Timedelta(days=1)
    data_analise = st.date_input('Período de análise', (data_inicio_dados, data_fim_dados))
    # converte para o formato data do pandas
    data_inicio = pd.to_datetime(data_analise[0])
    data_fim = pd.to_datetime(data_analise[1])
    # indicadores de acordo com as data de inicio e fim
    df_indicadores = ms.indicadores(data_inicio, data_fim)
    
    # dataframe com os dados
    st.dataframe(df_indicadores, use_container_width=True)

with tab_registro:
    # tabela editável
    with st.form("tabela_editavel"):
        ms = Manu()
        dados = ms.get_dados()
        de_dados = st.experimental_data_editor(dados, num_rows='dynamic', use_container_width=True)
        
        atualizar = st.form_submit_button("Atualizar")
        if atualizar:
            try:
                ms.set_dados(de_dados)
                st.info('A tabela foi atualizada com sucesso. 	✅')
            except Exception as e:
                st.error(e)