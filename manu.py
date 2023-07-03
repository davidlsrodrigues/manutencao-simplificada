import pandas as pd

class Manu:
    
    def __init__(self):
        self.__df_dados = pd.read_csv('dados/tabela_registro.csv', dtype=str)
        self.__df_dados_processados = self.__processar_dados(self.__df_dados)
    
    def get_dados(self):
        return self.__df_dados
    
    def get_dados_processados(self):
        return self.__processar_dados(self.__df_dados)
    
    def verificar_data(self, data):
        try:
            pd.to_datetime(data, format="%d/%m/%Y %H:%M:%S")
            return True
        except:
            return False
    
    def alterar_tabela(self, query):
        dados = self.get_dados()
        list_query = query.split(',')
        list_query = [x.strip().capitalize() for x in list_query]
        # INSERIR VALOR
        if list_query[0] == 'Inserir':
            equipamento = list_query[1]
            descritivo = list_query[2]
            if self.verificar_data(list_query[3]):
                abertura = list_query[3]
            else:
                raise ValueError('Formato de data inválido.')
            if len(list_query) == 5:
                if self.verificar_data(list_query[4]):
                    encerramento = list_query[4]
                    nova_linha = pd.DataFrame({'Equipamento':[equipamento],
                                               'Descritivo':[descritivo],
                                               'Abertura': [abertura],
                                               'Encerramento': [encerramento]})
                    dados = pd.concat([dados, nova_linha], axis=0)
                    dados.to_csv('dados/tabela_registro.csv', index=False)
                else:
                    raise ValueError('Formato de data inválido.')
            else:
                nova_linha = pd.DataFrame({'Equipamento':[equipamento],
                                           'Descritivo':[descritivo],
                                           'Abertura': [abertura]})
                dados = pd.concat([dados, nova_linha], axis=0)
                dados.to_csv('dados/tabela_registro.csv', index=False)
        # ATUALIZAR VALOR NO BANCO DE DADOS
        elif list_query[0] == 'Atualizar':
            index = int(list_query[1])
            coluna = list_query[2].capitalize()
            if coluna == 'Abertura' or coluna == 'Encerramento':
                if self.verificar_data(list_query[3]):
                    dados.iloc[index][coluna] = list_query[3]
                    dados.to_csv('dados/tabela_registro.csv', index=False)
                else:
                    raise ValueError('Formato de data inválido.')
            elif coluna == 'Equipamento' or coluna == 'Descritivo':
                dados.iloc[index][coluna] = list_query[3]
                dados.to_csv('dados/tabela_registro.csv', index=False)
            else:
                raise ValueError('Coluna inválida.')
        # REMOVER VALOR DO BANCO DE DADOS
        elif list_query[0] == 'Remover':
            index = int(list_query[1])
            if index < len(dados) and index >= 0:
                dados = dados.drop(index=index)
                dados.to_csv('dados/tabela_registro.csv', index=False)
            else:
                raise ValueError('Índice inexistente.')
        else:
            raise ValueError('Comando inválido.')
        
    def __processar_dados(self, df_dados):
        df_dados_processados = df_dados.copy()
        df_dados_processados = df_dados_processados.reset_index()
        df_dados_processados['Abertura'] = pd.to_datetime(df_dados_processados['Abertura'], format="%d/%m/%Y %H:%M:%S")
        df_dados_processados['Encerramento'] = pd.to_datetime(df_dados_processados['Encerramento'], format="%d/%m/%Y %H:%M:%S")
        df_dados_processados = df_dados_processados.sort_values(by='Encerramento')
        mt = df_dados_processados['Encerramento'] - df_dados_processados['Abertura']
        # converte o MT para horas no formato decimal.
        df_dados_processados['MT'] = mt.apply(lambda x: x.total_seconds() / 3600)
        return df_dados_processados
    
    def indicadores(self, data_inicio, data_fim):
        dados = self.__df_dados_processados.dropna(subset='Encerramento')
        dados = dados.loc[(data_inicio <= dados['Abertura'])&(dados['Abertura'] < data_fim)]
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
                tbf = (grupo['Abertura'].shift(-1) - grupo['Encerramento'])[:m-1]
                mtbf = sum(tbf.apply(lambda x: x.total_seconds() / 3600)) / (m - 1)
                dict_mtbf[equipamento] = round(mtbf, 2)
                dict_disponibilidade[equipamento] = round(mtbf/ (mttr+mtbf), 2)
            dict_paradas[equipamento] = m
            
        df_indicadores = pd.DataFrame({'MTTR':dict_mttr,
                                       'MTBF':dict_mtbf,
                                       'Disponibilidade':dict_disponibilidade,
                                       'Número Paradas':dict_paradas})
        return df_indicadores