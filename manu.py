import pandas as pd

class Manu:
    
    def __init__(self):
        self.__df_dados = pd.read_csv('dados/tabela_registro.csv', dtype=str, index_col=[0])
        self.__df_dados_processados = self.__processar_dados(self.__df_dados)
        
    def get_dados(self):
        return self.__df_dados
    
    def get_dados_processados(self):
        return self.__processar_dados(self.__df_dados)
    
    def set_dados(self, dados):
        self.__df_dados = dados
        self.__df_dados_processados = self.__processar_dados(dados)
        self.__df_dados.to_csv('dados/tabela_registro.csv')
        
    def __processar_dados(self, df_dados):
        df_dados_processados = df_dados.copy()
        df_dados_processados = df_dados_processados.reset_index()
        df_dados_processados['Data Abertura'] = pd.to_datetime(df_dados_processados['Data Abertura'], format="%d/%m/%Y %H:%M:%S")
        df_dados_processados['Data Encerramento'] = pd.to_datetime(df_dados_processados['Data Encerramento'], format="%d/%m/%Y %H:%M:%S")
        mt = df_dados_processados['Data Encerramento'] - df_dados_processados['Data Abertura']
        # converte o MT para horas no formato decimal.
        df_dados_processados['MT'] = mt.apply(lambda x: x.total_seconds() / 3600)
        return df_dados_processados
    
    def indicadores(self, data_inicio, data_fim):
        dados = self.__df_dados_processados
        dados = dados.loc[(data_inicio <= dados['Data Abertura'])&(dados['Data Abertura'] < data_fim)]
        dict_mttr = {}
        dict_mtbf = {}
        dict_disponibilidade = {}
        dict_paradas = {}
        dados_agrupados = dados.groupby('Equipamento')
        for equipamento, grupo in dados_agrupados:
            m = len(grupo)
            mttr = round(grupo['MT'].mean(), 2) if m >= 1 else None
            dict_mttr[equipamento] = mttr
            if m >= 2:
                tbf = (grupo['Data Abertura'].shift(-1) - grupo['Data Encerramento'])[:m-1]
                mtbf = sum(tbf.apply(lambda x: x.total_seconds() / 3600)) / m
                dict_mtbf[equipamento] = round(mtbf, 2)
                dict_disponibilidade[equipamento] = round(mtbf/ (mttr+mtbf), 2)
            dict_paradas[equipamento] = m
            
        df_indicadores = pd.DataFrame({'MTTR':dict_mttr,
                                       'MTBF':dict_mtbf,
                                       'Disponibilidade':dict_disponibilidade,
                                       'Número Paradas':dict_paradas})
        return df_indicadores