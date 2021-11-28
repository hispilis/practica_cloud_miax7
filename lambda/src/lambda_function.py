import pvpc_dao as dao

import json
from datetime import date

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
        result = dao_pvpc.get_range(p_start_date,p_end_date)        
        response = ''
        start_json = '{'
        for r in result:
            print(r)
            id_el  = r[0]['Dia']
            start_elem = f'"{id_el}":'
            elem = json.dumps(r)
            response = f'{response}{start_elem}{elem},'            
        response = response[:-1]
        end_json = '}'
        response = f'{start_json}{response}{end_json}'        
        print(response)                
    else:
        response = 'Parametro desconocido'
    return {
        'statusCode': 200,
        'body': response
    }

if __name__ == "__main__":
    event = {}
    event['multiValueQueryStringParameters'] = {'start_date': ['2016-11-28'], 'end_date': ['2021-11-28'], 'locale': ['es']}
    lambda_handler(event=event, context="")