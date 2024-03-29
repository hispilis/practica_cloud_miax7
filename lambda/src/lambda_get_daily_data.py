import pvpc_dao as dao

import pandas as pd
import requests
import json

from datetime import datetime

#Esta funcion actualiza diariamente la BD DynamoDB con el precio del dia
#Se despliega en AWS Lambda con docker

def handler(event, context):
    dao_pvpc = dao.PVPCDAO()
    url_base = 'https://api.esios.ree.es/archives/70/download_json?locale=es'
    now = datetime.now()
    end_date = datetime(year=now.year, month=now.month, day=now.day)
    url = f'{url_base}&date={end_date}'
    response = requests.get(url)
    df = pd.DataFrame(response.json()['PVPC'])
    for index, row in df.iterrows():                    
        split_dia = row['Dia'].split('/')
        row['Dia'] = f'{split_dia[2]}-{split_dia[1]}-{split_dia[0]}'
        dao_pvpc.insert_data(row.to_dict())
        response = dao_pvpc.get_data(row['Dia'])
        start_json = '{"PVPC":'
        end_json = '}'
        response = json.dumps(response)
        response = f'{start_json}{response}{end_json}'
    print(response)
    return {
        'statusCode': 200,
        'body': response
    }
    
if __name__ == "__main__":
    handler(event="", context="")    
