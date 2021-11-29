import requests
import json
import logging
import pandas as pd
from datetime import date

class APIESIOS:
    
    def __init__(self, url_base):
        self.url_base = url_base
    
    def get_daily_data(self, date):
        url = f'{self.url_base}&date={date}'
        print(url)
        response = requests.get(url)
        print(response)
        df = pd.DataFrame(response.json()['PVPC'])
        df['Hora'] = df['Hora'].str[:2]
        if 'PCB' in df.columns:
            df['PCB'] = df['PCB'].str.replace(',','.').astype('float')
            return df[['Hora','PCB']]
        elif 'GEN' in df.columns:
            df['GEN'] = df['GEN'].str.replace(',','.').astype('float')
            return df[['Hora','GEN']]

    def get_range_data(self, start_date, end_date):
        url = f'{self.url_base}&start_date={start_date}&end_date={end_date}'
        print(url)
        response = requests.get(url)
        response = response.json()                
        serie = pd.Series(response)
        serie.name = 'pvpc_medio'
        serie.sort_index(inplace=True)
        print(serie)        
        return serie

if __name__ == "__main__":
    api = APIESIOS('https://z7n1qubz0k.execute-api.eu-west-3.amazonaws.com/default/api_data_pvpc?locale=es')
    print(api.get_daily_data('2021-11-28'))
    print(api.get_range_data('2021-11-25','2021-11-28'))