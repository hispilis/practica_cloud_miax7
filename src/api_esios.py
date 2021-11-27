import requests
import json
import logging
import pandas as pd

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
        