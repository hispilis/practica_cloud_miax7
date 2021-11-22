import requests
import json
import logging
import pandas as pd

class APIESIOS:
    
    def __init__(self):
        self.url_base = 'https://api.esios.ree.es/archives/70/download_json?locale=es'

    def get_data(self, date):
        url = f'{self.url_base}&date={date}'
        response = requests.get(url)
        df = pd.DataFrame(response.json()['PVPC'])
        df['Hora'] = df['Hora'].str[:2]
        if 'PCB' in df.columns:
            df['PCB'] = df['PCB'].str.replace(',','.').astype('float')
            return df[['Hora','PCB']]
        elif 'GEN' in df.columns:
            df['GEN'] = df['GEN'].str.replace(',','.').astype('float')
            return df[['Hora','GEN']]
        