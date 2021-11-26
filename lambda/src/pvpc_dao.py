import pandas as pd
import boto3
from boto3.dynamodb.conditions import Key

import requests
import json
import logging
import pandas as pd

from datetime import datetime
from datetime import timedelta

class PVPCDAO:
    
    def __init__(self):
        self.dynamo_db = boto3.resource('dynamodb')
        try:
            self.table = self.dynamo_db.create_table(
                TableName = 'PVPC',

                #"GEN":"120,67","NOC":"70,37","VHC":"75,42","COFGEN":"0,000111396270000000","COFNOC":"0,000156785536000000","COFVHC":"0,000138602057000000","PMHGEN":"64,06","PMHNOC":"60,87","PMHVHC":"64,46","SAHGEN":"4,33","SAHNOC":"4,12","SAHVHC":"4,36","FOMGEN":"0,03","FOMNOC":"0,03","FOMVHC":"0,03","FOSGEN":"0,18","FOSNOC":"0,17","FOSVHC":"0,18","INTGEN":"0,00","INTNOC":"0,00","INTVHC":"0,00","PCAPGEN":"5,87","PCAPNOC":"0,97","PCAPVHC":"1,39","TEUGEN":"44,03","TEUNOC":"2,22","TEUVHC":"2,88","CCVGEN":"2,17","CCVNOC":"1,99","CCVVHC":"2,11"},{"Dia":"01/01/2021","Hora":"01-02","GEN":"117,38","NOC":"67,36","VHC":"63,67","COFGEN":"0,000093667286000000","COFNOC":"0,000140250815000000","COFVHC":"0,000153300578000000","PMHGEN":"60,26","PMHNOC":"57,35","PMHVHC":"55,44","SAHGEN":"4,92","SAHNOC":"4,68","SAHVHC":"4,53","FOMGEN":"0,03","FOMNOC":"0,03","FOMVHC":"0,03","FOSGEN":"0,18","FOSNOC":"0,17","FOSVHC":"0,17","INTGEN":"0,00","INTNOC":"0,00","INTVHC":"0,00","PCAPGEN":"5,84","PCAPNOC":"0,97","PCAPVHC":"0,75","TEUGEN":"44,03","TEUNOC":"2,22","TEUVHC":"0,89","CCVGEN":"2,11","CCVNOC":"1,94","CCVVHC":"1,87"}

                KeySchema = [
                    {
                        'AttributeName' : 'Dia',
                        'KeyType' : 'HASH'
                    },
                    {
                        'AttributeName' : 'Hora',
                        'KeyType' : 'RANGE'
                    }
                ],
                AttributeDefinitions=[
                    {
                        'AttributeName' : 'Dia',
                        'AttributeType' : 'S'
                    },
                    {
                        'AttributeName' : 'Hora',
                        'AttributeType' : 'S'
                    }
                ],
                ProvisionedThroughput={ 
                    'ReadCapacityUnits': 10, 
                    'WriteCapacityUnits': 10 
                }
            )
        except Exception as e:
            #print(e)
            self.table = self.dynamo_db.Table('PVPC')
    
    def insert_data(self, item):
        response = self.table.put_item(
            Item=item
        )
        return response

    def get_data(self, date):        
        self.table = self.dynamo_db.Table('PVPC')
        response = self.table.query(
            KeyConditionExpression=Key('Dia').eq(date)
        )
        #df = pd.DataFrame(response['Items'])
        #eturn df
        return response['Items']

if __name__ == "__main__":
    try:
        dao = PVPCDAO()
                
        date = '01/01/2020'

        url_base = 'https://api.esios.ree.es/archives/70/download_json?locale=es'

        now = datetime.now()

        end_date = datetime(year=now.year, month=now.month, day=now.day)
        start_date = datetime(year=(now.year - 5), month=now.month, day=now.day)
        
        delta = timedelta(days=1)

        while start_date <= end_date:
            print(start_date)
            date = start_date
            start_date += delta
            url = f'{url_base}&date={date}'
            response = requests.get(url)
            df = pd.DataFrame(response.json()['PVPC'])
            for index, row in df.iterrows():                    
                print(row.to_dict())
                dao.insert_data(row.to_dict())            
                #response = dao.get_data(row['Dia'])
                #print(response)

    except Exception as e: 
        print("Caught exception:", e)