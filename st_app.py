import streamlit as st
from manu import Manu
from matplotlib import pyplot as plt
import pandas as pd
import math

plt.style.use('default')
st.set_page_config(layout='wide')

# funções
ms = Manu()

st.title('Manu')

# descrição
txt_descricao = 'De uma tabela com quatro colunas, obtenha *insights* incríveis de manutenção! ⚙️❇️\n'
st.write(txt_descricao)

tab_indicador, tab_registro, tab_guia = st.tabs(['📊 Indicadores', '📝 Registros', '❓ Guia básico sobre indicadores'])

with tab_indicador:
    
    # periodo padrão de analise
    try:
        data_inicio_dados = ms.get_dados_processados()['Abertura'].min()
        data_hoje = pd.to_datetime('today', format='%d/%m/%Y')
        data_analise = st.date_input('Período de análise', (data_inicio_dados, data_hoje), max_value=data_hoje)
    
    
        if len(data_analise) == 2:
            # converte para o formato data do pandas
            data_inicio = pd.to_datetime(data_analise[0])
            data_fim = pd.to_datetime(data_analise[1])
            
            # indicadores de acordo com as data de inicio e fim
            df_indicadores = ms.indicadores(data_inicio, data_fim)
            
            # indicadores da planta
            st.caption('Desempenho médio dos equipamentos.')
            mttr_media = round(df_indicadores['MTTR'].mean(), 2)
            mtbf_media = round(df_indicadores['MTBF'].mean(), 2)
            disponibilidade_media = round(df_indicadores['Disponibilidade'].mean(), 2)
            total_numero_paradas = df_indicadores['Número Paradas'].sum()
            
            col_mttr, col_mtbf, col_disponibilidade, col_numero_paradas = st.columns(4)
            col_mttr.metric('MTTR [h]', mttr_media)
            col_mtbf.metric('MTBF [h]', mtbf_media)
            col_disponibilidade.metric('Disponibilidade', disponibilidade_media)
            col_numero_paradas.metric('Número Paradas (Finalizadas)', total_numero_paradas)
            
            # gráfico com mttr, mtbf e disponibilidade
            st.caption('Gráfico de cada equipamento')
            g_mttr, g_mtbf, g_disp = st.columns(3)
            with g_mttr:
                fig, ax = plt.subplots()
                df_indicadores['MTTR'].plot(kind='bar', title='MTTR', xlabel='Equipamento', ylabel='MTTR [h]')
                st.pyplot(fig)
                
            with g_mtbf:
                fig, ax = plt.subplots()
                df_indicadores['MTBF'].plot(kind='bar', title='MTBF', xlabel='Equipamento', ylabel='MTBF [h]')
                st.pyplot(fig)
                
            with g_disp:
                fig, ax = plt.subplots()
                df_indicadores['Disponibilidade'].plot(kind='bar', title='Disponibilidade', xlabel='Equipamento', ylabel='Disponibilidade [%]')
                st.pyplot(fig)
            
            # confiabilidade
            dict_confiabilidade = {}
            dados_processados = ms.get_dados_processados()
            for equipamento in df_indicadores.index:
                ultima_manutencao = dados_processados.loc[dados_processados['Equipamento']==equipamento, 'Encerramento'].values[-1]
                if ultima_manutencao == None:
                    dict_confiabilidade[equipamento] = [0]
                else:
                    delta_t = (data_hoje - ultima_manutencao).total_seconds() / 3600
                    taxa_falha = 1 / df_indicadores.loc[equipamento]['MTBF']
                    confiabilidade = round(math.e**(-delta_t*taxa_falha), 2)
                    dict_confiabilidade[equipamento] = [confiabilidade]
                
            df_confiabilidade = pd.DataFrame(dict_confiabilidade).T
            df_confiabilidade.columns = ['Confiabilidade']
            
            col_conf, col_dados = st.columns(2)
            
            with col_conf:
                # confiabilidade dos equipamentos
                st.caption('Confiabilidade')
                st.dataframe(df_confiabilidade, use_container_width=True)
            
            with col_dados:
                # dataframe com os dados
                st.caption('Outros indicadores')
                st.dataframe(df_indicadores, use_container_width=True)
        else:
            st.warning('⏰ Aguardando seleção das datas.')
    
    except:
        st.error('Não foi possível recuperar as informações do banco de dados. Verifique se existem registros com informações completas no banco.')
        
with tab_registro:
    with st.form("registro"):
        ms = Manu()
        dados = ms.get_dados()
        st.dataframe(dados, use_container_width=True)
        
        with st.expander('Como usar a caixa função?', expanded=False):
            st.write('Você pode executar os seguintes comandos:')
            st.write('"INSERIR, *equipamento*, *descritivo*, *data_abertura*, *data_encerramento*". Para manutenções em aberto, a data_encerramento pode ser omitida.')
            st.write('"ATUALIZAR, *indice*, *coluna*, *novo_valor*". Atualiza um registro com base na coluna, índice e no novo valor informado.')
            st.write('"REMOVER, *indice*". Remove um registro com base no índice informado.')
            st.write('Índices devem ser valores numéricos e as datas devem seguir o formato dd/mm/aaaa HH\:MM\:SS.')
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
                
with tab_guia:
    """
    **MTTR** (Mean Time to Repair ou Tempo Médio de Reparo): É o tempo médio necessário para reparar uma falha ou problema em um sistema. Basicamente, representa o tempo médio que leva para consertar algo que tenha apresentado algum defeito. Quanto menor o MTTR, mais rápido o sistema pode ser restaurado após uma falha.
    \n**MTBF** (Mean Time Between Failures ou Tempo Médio entre Falhas): É o tempo médio decorrido entre duas falhas consecutivas em um sistema. Em outras palavras, é o tempo médio em que um sistema funciona continuamente sem apresentar falhas. O MTBF é um indicador da confiabilidade de um sistema, pois quanto maior o MTBF, mais tempo o sistema tende a operar sem falhas.
    \n**Confiabilidade**: É a capacidade de um sistema ou componente de desempenhar suas funções especificadas sem falhas durante um determinado período de tempo. A confiabilidade é geralmente expressa como a probabilidade de que um sistema funcione corretamente dentro de certos parâmetros ao longo de um determinado período. Quanto maior a confiabilidade de um sistema, menor a probabilidade de ocorrerem falhas.
    \n**Disponibilidade**: É a capacidade de um sistema ou componente estar disponível e em pleno funcionamento quando necessário. Está relacionada ao tempo em que um sistema está operacional e pronto para ser utilizado. A disponibilidade é influenciada pelo MTBF e pelo MTTR, pois quanto maior o MTBF (tempo médio entre falhas) e menor o MTTR (tempo médio de reparo), maior será a disponibilidade do sistema.")
    """
