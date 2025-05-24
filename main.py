from app.AWSConnections import AWSConnections
import boto3
from dotenv import load_dotenv
import os
import requests
from decimal import Decimal

load_dotenv()   #se carga el acrhivo .env

apiKey = os.getenv('API_KEY')   #se saca la key de la api

dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
table = dynamodb.Table('Users_firstTable')

print(f"---- Bienvenido a INVERSIONES URL ----")
mainmenu = input("Ingresa el numero correspondiente a la acción que deseas realizar\n1. - Iniciar sesion\n2. - Registrarme\n3. - Salir\n")

def actionsList():
    actions = {
        'Microsoft': 'MSFT',
        'Samsung': 'SSNLF',
        'Tesla': 'TSLA',
        'Nvidia': 'NVDA',
        'Toyota': 'TYO'
    }

    precios = {}

    for name, symbol in actions.items():
        url = f"https://api.twelvedata.com/price?symbol={symbol}&apikey={apiKey}"
        resp = requests.get(url).json()
        if 'price' in resp:
            print(f"El precio actual de {name} ({symbol}) es: ${resp['price']}")
            precios[symbol] = Decimal(resp['price'])  # 💡 Guardamos el precio en el dict
        else:
            print(f"No se pudo obtener el precio de {name} ({symbol})")

    return precios

def newMoney():
  dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
  table = dynamodb.Table('Users_firstTable')
  respuesta = table.update_item(
    Key={'email': usuario_id},
    UpdateExpression="SET money = :nuevo_saldo",
    ExpressionAttributeValues={':nuevo_saldo': finalMoney},
    ReturnValues="UPDATED_NEW"
  )

  print("--- 💰 Saldo actualizado exitosamente. ---")
  print("Nuevo saldo:", respuesta['Attributes']['money'])

resp = actionsList

if mainmenu == "1":
    userExist = False
    while userExist == False:
        load_dotenv()
        "aws_access_key_id" == os.getenv("aws_access_key_id")
        "aws_secret_access_key" == os.getenv("aws_secret_access_key")
        
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')

        table = dynamodb.Table('Users_firstTable')

        usuario_id = input("Ingresa tu correo: ")

        respuesta = table.get_item(Key={"email": usuario_id})

        usuario = respuesta.get('Item')

        if usuario:
            print("Usuario encontrado:")
            print(f"--- Bienvenido {usuario['name']}! - Tu saldo es de {usuario['money']} ---")
            money = usuario['money']
            userExist = True
        else:
            print("Usuario no encontrado.")

elif mainmenu == "2":
    aws = AWSConnections()
    awsSession = aws.getSession()

    def saveUserDynamoDB(session, user_data):
      dynamodb = session.resource('dynamodb')
      table = dynamodb.Table('Users_firstTable')
      response = table.put_item(Item=user_data)

      return response, table, print("Te has registrado con éxito! Recibiste $15,000")

    email = usuario_id = input("Ingresa tu correo electrónico: ")
    name = input("Ingrese su nombre: ")
    money = 15000
    user_item = {"email": email, "name": name, "money": money}

    saveUserDynamoDB(awsSession, user_item)

elif mainmenu == "3":
   print("Gracias por vicitar inverisones pepito")
   exit()

WhatDo = input(f"Que deseas realizar?\n1. - Comprar acciones\n2. - Vender acciones\n3. - Salir\n")
if WhatDo == "1":
    actionsPrice = actionsList()
    action = input("¿Qué acción quieres comprar? (Ingresa las letras)\n").upper()

    if action in actionsPrice:
        money = Decimal(str(money))
        actionPrice = actionsPrice[action]
        finalMoney = money - actionPrice
        newMoney()
    else:
        print("Acción no válida o no disponible.")
