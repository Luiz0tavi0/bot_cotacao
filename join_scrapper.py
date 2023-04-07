import datetime
import pandas as pd
import os

# Esse script destinasse a junção de todas as planilhas de todas em uma só


COLUNA_PRODUTO = 'Produto' # Nome da coluna em que estarão os produtos

# Define a ordem em que cada coluna aparecerá no arquivo ao final
columns_in_order = ['Link {}', 'Disponibilidade {}', 'Preço Promoção {}', 'Preço Normal {}', 'Unidade {}', 'ID {}']


def open_and_rename_dfs_columns(list_to_files):
    dfs = []
    for file in list_to_files:
        df = pd.read_excel(file)
        del df['Site']
        name_fornecedor = file.split('_spider_output')[0]
        df = df.add_suffix(f' {name_fornecedor}')

        columns = [f'{COLUNA_PRODUTO} {name_fornecedor}'] + [col.format(name_fornecedor) for col in columns_in_order]
        df = df[columns]
        df.rename(columns={f'{COLUNA_PRODUTO} {name_fornecedor}': COLUNA_PRODUTO}, inplace=True)

        dfs.append(df)
    return dfs


def get_all_products_without_repetition(list_dfs):
    list_products = []
    for df in list_dfs:
        list_products.extend(df[COLUNA_PRODUTO].to_list())

    list_products = list(set(list_products))
    return list_products


def make_final_df_result(list_products: list):
    df_result = pd.DataFrame(list_products, columns=([COLUNA_PRODUTO]))
    return df_result


def join_dataframes_on_product(df_result, list_dfs):
    for df in list_dfs:
        df_result = pd.merge(df_result, df, how='outer', on=COLUNA_PRODUTO)
    return df_result


def join_all_results():
    list_files = [file for file in os.listdir('.') if file.endswith('output.xlsx') and not (file.startswith('~$'))]
    # Coleta todos os nomes de arquivos que terminam com 'output.xlsx' pois são os resultados do scrapp por
    # homecenter/fornecedor

    dfs = open_and_rename_dfs_columns(list_files)
    list_with_all_products = get_all_products_without_repetition(dfs)

    df = make_final_df_result(list_with_all_products)
    # cria o dataframe que será exportado ao final

    df = join_dataframes_on_product(df_result=df, list_dfs=dfs)
    # junta cada dataframe com base no produto

    df.sort_values(by=[COLUNA_PRODUTO], inplace=True)

    df.to_excel(f'precos_{datetime.datetime.now().strftime("%d-%m-%Y_%Hh%Mm%Ss")}.xlsx', index=False)
    # Exporta para excel o arquivo no formato precos_{dia_atual}-mes_atual-ano_atual_horah00minuto00segundo.xlsx
    # exemplo -> precos_27-03-2023_16h00m00s.xlsx


if __name__ == '__main__':
    # para executar apenas a coleta e junção dos arquivos de output de cada site, os com final "_spider_output.xlsx"
    # execute esse arquivo com
    # python join_scrapper.py
    join_all_results()
