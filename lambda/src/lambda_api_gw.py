import json
from datetime import date
from datetime import datetime
import boto3
from boto3.dynamodb.conditions import Key

#Esta funcion usa librerias basicas que vienen ya instaladas en AWS Lambda
#No se va a desplegar con docker. 
#Deberia usar la clase DAO, pero para ahorrar el despliegue con docker duplicamos el acceso a DynamoDB

def lambda_handler(event, context):
    # TODO implement
    dynamo_db = boto3.resource('dynamodb')
    table = dynamo_db.Table('PVPC')
    params = event.get('multiValueQueryStringParameters')
    if params is None:
        response = 'Incluye un parametro'
    elif 'date' in params:
        p_date = params['date'][0]
        str_date = p_date.split("-")
        date_object = date(year=int(str_date[0]), month=int(str_date[1]), day=int(str_date[2]))
        date_string = date_object.strftime('%d/%m/%Y')
        print(date_string)
        response = table.query(
            KeyConditionExpression=Key('Dia').eq(date_string)
        )
        print(response)
        response = response['Items']
        print(response)
        start_json = '{"PVPC":'
        end_json = '}'
        response = json.dumps(response)
        print(response)
        response = f'{start_json}{response}{end_json}'
        print(response)
    elif 'start_date' in params and 'end_date' in params:
        p_from = params['start_date'][0]
        p_to = params['end_date'][0]
        response = json.dumps(f' from: {p_from} to: {p_to}')
        
        p_from = params['start_date'][0]
        str_from = p_from.split("-")
        date_object = date(year=int(str_from[0]), month=int(str_from[1]), day=int(str_from[2]))
        date_string_from = date_object.strftime('%Y-%m-%d')
        
        p_to = params['end_date'][0]
        str_to = p_to.split("-")
        date_object = date(year=int(str_to[2]), month=int(str_to[1]), day=int(str_to[2]))
        date_string_to = date_object.strftime('%Y-%m-%d')
        
        query_range = (date_string_from, date_string_to)
        
        print(*query_range)
        
        scan_kwargs = {
            'FilterExpression': Key('Dia_ISO').between(*query_range)
        }
    
        done = False
        start_key = None
        result = []
        while not done:
            if start_key:
                scan_kwargs['ExclusiveStartKey'] = start_key
            response = table.scan(**scan_kwargs)
            res = response.get('Items', [])
            if len(res) > 0:
                result.append(res)
            start_key = response.get('LastEvaluatedKey', None)
            done = start_key is None
        
        print(result)
        response = ''
        start_json = '{'
        for r in result:
            print(r)
            id_el  = r[0]['Dia']
            start_elem = f'"{id_el}":'
            elem = json.dumps(r)
            response = f'{response}{start_elem}{elem},'
            print(response)
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
