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
        date_object = date(int(str_date[2]), int(str_date[1]), int(str_date[0]))
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
    elif 'from' in params and 'to' in params:
        p_from = params['from'][0]
        p_to = params['to'][0]
        response = json.dumps(f' from: {p_from} to: {p_to}')
    else:
        response = 'Parametro desconocido'
    return {
        'statusCode': 200,
        'body': response
    }
