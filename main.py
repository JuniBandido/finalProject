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

mainmenu = input("Ingrese el numero correspondiente a la acción que desea realizar\n1. - Iniciar sesion\n2. - Registrarme\n3. - Salir\n")

def actionsList():
        actions = {
            'Microsoft': 'MSFT',
            'Samsung': 'SSNLF',
            'Tesla': 'TSLA',
            'Nvidia': 'NVDA',
            'Toyota': 'TM'  
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

        print("---- Saldo actualizado ----")
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

            usuario_id = input("Ingrese su correo: ")

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

            return response, table, print("Se ha registrado con éxito! Recibio $15,000")

        email = usuario_id = input("Ingrese su correo electrónico: ")
        name = input("Ingrese su nombre: ")
        money = 15000
        user_item = {"email": email, "name": name, "money": money}

        saveUserDynamoDB(awsSession, user_item)

elif mainmenu == "3":
        print("Gracias por vicitar inverisones URL")
        exit()

programRunning = True
while programRunning == True:

    WhatDo = input(f"Que desea realizar?\n1. - Comprar acciones\n2. - Vender acciones\n3. - Ver resumen de inversión\n4. - Salir\n")
    if WhatDo == "1":
        actionsPrice = actionsList()
        action = input("¿Qué acción desea comprar? (Por favor ingrese las letras)\n").upper()

        if action in actionsPrice:
            money = Decimal(str(money))
            actionPrice = actionsPrice[action]
            finalMoney = money - actionPrice

            # Actualizar portafolio
            respuesta = table.get_item(Key={"email": usuario_id})
            usuario = respuesta.get('Item')
            portfolio = usuario.get('portfolio', {})
            if action in portfolio:
                portfolio[action] += 1
            else:
                portfolio[action] = 1

            table.update_item(
                Key={'email': usuario_id},
                UpdateExpression="SET money = :nuevo_saldo, investment = :inversion, portfolio = :portafolio",
                ExpressionAttributeValues={
                    ':nuevo_saldo': finalMoney,
                    ':inversion': actionPrice,
                    ':portafolio': portfolio
                },
                ReturnValues="UPDATED_NEW"
            )
            print(f"----Compra realizada con éxito----")
            newMoney()

        else:
            print("Lo sentimos su acción no es válida.")

    elif WhatDo == "2":
        actionsPrice = actionsList()

        # Mostrar portafolio antes de vender
        respuesta = table.get_item(Key={"email": usuario_id})
        usuario = respuesta.get('Item')
        portfolio = usuario.get('portfolio', {})
        if portfolio:
            print("Acciones disponibles para vender:")
            for accion, cantidad in portfolio.items():
                print(f"{accion}: {cantidad}")
        else:
            print("No tienes acciones para vender.")

        action = input("¿Qué acción desea vender? (Ingresa las letras)\n").upper()

        if action in actionsPrice:
            investment = Decimal(str(usuario.get('investment', 0)))
            actionPrice = actionsPrice[action]
            money = Decimal(str(usuario['money']))

            if portfolio.get(action, 0) > 0:
                finalMoney = money + actionPrice
                portfolio[action] -= 1
                if portfolio[action] == 0:
                    del portfolio[action]

                table.update_item(
                    Key={'email': usuario_id},
                    UpdateExpression="SET money = :nuevo_saldo, portfolio = :portafolio REMOVE investment",
                    ExpressionAttributeValues={
                        ':nuevo_saldo': finalMoney,
                        ':portafolio': portfolio
                    },
                    ReturnValues="UPDATED_NEW"
                )
                print(f"Se ha vendido {action} por ${actionPrice}.")
            else:
                print("----No tiene esa acción en su portafolio para vender----")
        else:
            print("----Acción no disponible----")

    elif WhatDo == "3":
        def resumenInversion():
            respuesta = table.get_item(Key={"email": usuario_id})
            usuario = respuesta.get('Item')

            if usuario:
                print(f"---Resumen de Inversión de {usuario['name']} ---")
                portfolio = usuario.get('portfolio', {})
                if portfolio == usuario['portfolio']:
                        print("Acciones en las que ha invertido:")
                        for accion, cantidad in usuario['portfolio'].items():
                            print(f"{accion}: {cantidad}")
                else:
                    print("Aún no ha invertido en ninguna acción.")
                print(f"Saldo disponible: ${usuario['money']}")
            else:
                print("Usuario no encontrado.")
        resumenInversion()

    elif WhatDo == "4":
        print("Saliendo...")
        exit()
        programRunning = False