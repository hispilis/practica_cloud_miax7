import pvpc_dao as dao

import json
from datetime import date,datetime,timedelta

import pandas as pd
#Esta funcion se utiliza enlazada con API GATEWAY como API del servicio
#No se va a desplegar con docker

def lambda_handler(event, context):
    dao_pvpc = dao.PVPCDAO()
    params = event.get('multiValueQueryStringParameters')
    if params is None:
        response = 'Incluye un parametro'
    elif 'date' in params:
        p_date = params['date'][0]        
        response = dao_pvpc.get_data(p_date)        
        start_json = '{"PVPC":'
        end_json = '}'
        response = json.dumps(response)        
        response = f'{start_json}{response}{end_json}'
        print(response)
    elif 'start_date' in params and 'end_date' in params:
        p_start_date = params['start_date'][0]
        p_end_date = params['end_date'][0]                    
                        
        end_date = datetime.strptime(p_end_date, '%Y-%m-%d')
        start_date = datetime.strptime(p_start_date, '%Y-%m-%d')
        delta = timedelta(days=1)

        #response = dao_pvpc.get_range(p_start_date,p_end_date)
        #Me veo obligado a usar este while por el mal comportamiento del scan para DynamboDB
        response = []
        while start_date <= end_date:
            date_object = start_date
            start_date += delta                        
            result = dao_pvpc.get_data(date_object.strftime('%Y-%m-%d'))            
            response.append(result)        
        
        result = {}
        for r in response:            
            df = pd.DataFrame(r)                
            mean = 0
            if 'PCB' in df.columns:
                df['PCB'] = df['PCB'].str.replace(',','.').astype('float')
                mean =  df['PCB'].mean()                
            elif 'GEN' in df.columns:
                df['GEN'] = df['GEN'].str.replace(',','.').astype('float')
                mean =  df['GEN'].mean()                
            str_date = r[0]['Dia'].split("-")                        
            date_object = date(year=int(str_date[0]), month=int(str_date[1]), day=int(str_date[2]))                        
            result[date_object] = mean
        serie = pd.Series(result)
        serie.name = 'pvpc_medio'
        serie.sort_index(inplace=True)                
        response=serie.to_json(date_format='iso')            
        print(response)
    else:
        response = 'Parametro desconocido'
    return {
        'statusCode': 200,
        'body': response
    }

if __name__ == "__main__":
    event = {}
    event['multiValueQueryStringParameters'] = {'start_date': ['2021-10-29'], 'end_date': ['2021-11-28'], 'locale': ['es']}
    lambda_handler(event=event, context="")