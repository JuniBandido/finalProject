from app.AWSConnections import AWSConnections
import boto3
from dotenv import load_dotenv
import os
import requests
from decimal import Decimal
import time
from colorama import init, Fore, Style
init(autoreset=True)

load_dotenv()   # se carga el archivo .env

apiKey = os.getenv('API_KEY')   # se saca la key de la api

dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
table = dynamodb.Table('Users_firstTable')

print(Fore.BLUE + "---- Bienvenido a INVERSIONES URL ----")

mainmenu = input(Fore.YELLOW + "Ingrese el numero correspondiente a la acción que desea realizar\n1. - Iniciar sesion\n2. - Registrarme\n3. - Salir\n")

# Función para imprimir con color segun nivel
def print_color(text, level='NORMAL'):
    colors = {
        'INFO': '\033[94m',      # Azul claro
        'ERROR': '\033[91m',     # Rojo
        'WARNING': '\033[93m',   # Amarillo
        'NORMAL': '\033[0m'      # Normal (reset)
    }
    color = colors.get(level, colors['NORMAL'])
    reset = '\033[0m'
    print(f"{color}{text}{reset}")

def actionsList():
    actions = {
        'Microsoft': 'MSFT',    # diccionaro con los nombres 
        'Samsung': 'SSNLF',
        'Tesla': 'TSLA',
        'Nvidia': 'NVDA',
        'Toyota': 'TM'  
    }

    precios = {}

    for name, symbol in actions.items():
        intentos = 3
        while intentos > 0:
            try:
                url = f"https://api.twelvedata.com/price?symbol={symbol}&apikey={apiKey}"  # api url de precios
                resp = requests.get(url, timeout=5)
                data = resp.json()
                if 'price' in data and data['price'] not in [None, 'None', '', 'null']:
                    print_color(Fore.BLUE + f"[INFO] Precio actual de {name} ({symbol}): ${data['price']}",)  # precios obtenidos
                    precios[symbol] = Decimal(data['price'])
                    intentos = 0
                else:
                    error_msg = data.get('message', 'Respuesta inválida.')
                    print_color(Fore.RED + f"[ERROR] No se pudo obtener el precio de {name} ({symbol}): {error_msg}",)
                    intentos = 0
            except Exception as e:
                intentos -= 1
                if intentos == 0:
                    print_color(f"[ERROR] No se pudo obtener el precio de {name} ({symbol}) tras varios intentos.", 'ERROR')
                else:
                    time.sleep(2)
        time.sleep(2)  # tiempo de espera entre cada acción
    return precios

def newMoney():
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('Users_firstTable')
    respuesta = table.update_item(
        Key={'email': usuario_id},    # clave primaria del email
        UpdateExpression="SET money = :nuevo_saldo",  # actializa el saldo
        ExpressionAttributeValues={':nuevo_saldo': finalMoney},
        ReturnValues="UPDATED_NEW"
    )

    print_color(Fore.MAGENTA + "---- Saldo actualizado ----", 'INFO')
    print_color(f"Nuevo saldo: {respuesta['Attributes']['money']}", 'INFO')

resp = actionsList

if mainmenu == "1":
    userExist = False
    while userExist == False:
        load_dotenv()   # recarga variables
        "aws_access_key_id" == os.getenv("aws_access_key_id")  # carga las credenciales aws
        "aws_secret_access_key" == os.getenv("aws_secret_access_key")
        
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')

        table = dynamodb.Table('Users_firstTable')

        usuario_id = input("Ingrese su correo: ")   # pide el email

        respuesta = table.get_item(Key={"email": usuario_id})

        usuario = respuesta.get('Item')

        if usuario:
            print_color("Usuario encontrado:", 'INFO')
            print_color(Fore.CYAN + f"--- Bienvenido {usuario['name']}! - Tu saldo es de {usuario['money']} ---", 'INFO')
            money = usuario['money']   # muestra el saldo actual
            userExist = True
        else:
            print_color("Usuario no encontrado.", 'ERROR')

elif mainmenu == "2":
    aws = AWSConnections()
    awsSession = aws.getSession()

    def saveUserDynamoDB(session, user_data):
        dynamodb = session.resource('dynamodb')
        table = dynamodb.Table('Users_firstTable')
        response = table.put_item(Item=user_data)

        print_color("Se ha registrado con éxito! Recibio $15,000", 'INFO')
        return response, table

    email = usuario_id = input("Ingrese su correo electrónico: ")  # pedi datos registrados
    name = input("Ingrese su nombre: ")
    money = 15000   # muestra el saldo
    user_item = {"email": email, "name": name, "money": money}

    saveUserDynamoDB(awsSession, user_item)

elif mainmenu == "3":
    print_color("Gracias por vicitar inverisones URL", 'INFO')
    exit()

programRunning = True
while programRunning == True:

    WhatDo = input(Fore.MAGENTA + f"Que desea realizar?\n1. - Comprar acciones\n2. - Vender acciones\n3. - Ver resumen de inversión\n4. - Salir\n")
    if WhatDo == "1":
        actionsPrice = actionsList()
        action = input(Fore.LIGHTCYAN_EX + "¿Qué acción desea comprar? (Por favor ingrese las letras)\n").upper()

        if action in actionsPrice:
            money = Decimal(str(money))
            actionPrice = actionsPrice[action]
            finalMoney = money - actionPrice    # actualiza el saldo despues de la compra

            respuesta = table.get_item(Key={"email": usuario_id})
            usuario = respuesta.get('Item')
            portfolio = usuario.get('portfolio', {})
            history = usuario.get('history', [])

            if action in portfolio:
                portfolio[action] += 1   # suma las acciones
            else:
                portfolio[action] = 1

            # guarda el historial de compras
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            history.append({
                "type": "compra",
                "accion": action,
                "precio": str(actionPrice),
                "fecha": timestamp
            })

            table.update_item(
                Key={'email': usuario_id},
                UpdateExpression="SET money = :nuevo_saldo, portfolio = :portafolio, history = :historial",
                ExpressionAttributeValues={
                    ':nuevo_saldo': finalMoney,
                    ':portafolio': portfolio,
                    ':historial': history
                },
                ReturnValues="UPDATED_NEW"
            )
            print_color(f"----Compra realizada con éxito----", 'INFO')
            newMoney()

        else:
            print_color("Lo sentimos su acción no es válida.", 'ERROR')

    elif WhatDo == "2":
        actionsPrice = actionsList()

        respuesta = table.get_item(Key={"email": usuario_id})
        usuario = respuesta.get('Item')
        portfolio = usuario.get('portfolio', {})
        history = usuario.get('history', [])

        if portfolio:
            print_color("Acciones disponibles para vender:", 'INFO')
            for accion, cantidad in portfolio.items():
                print_color(f"{accion}: {cantidad}", 'NORMAL')
        else:
            print_color("No tienes acciones para vender.", 'WARNING')
            pass

        action = input("¿Qué acción desea vender? (Ingresa las letras)\n").upper()

        if action in actionsPrice:
            investment = Decimal(str(usuario.get('investment', 0)))
            actionPrice = actionsPrice[action]
            money = Decimal(str(usuario['money']))

            if portfolio.get(action, 0) > 0:
                finalMoney = money + actionPrice    # muestra el saldo despues de alguna venta
                portfolio[action] -= 1
                if portfolio[action] == 0:
                    del portfolio[action]

                # guarda el historial de venta
                timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                history.append({
                    "type": "venta",
                    "accion": action,
                    "precio": str(actionPrice),
                    "fecha": timestamp
                })

                table.update_item(
                    Key={'email': usuario_id},
                    UpdateExpression="SET money = :nuevo_saldo, portfolio = :portafolio, history = :historial REMOVE investment",
                    ExpressionAttributeValues={
                        ':nuevo_saldo': finalMoney,
                        ':portafolio': portfolio,
                        ':historial': history
                    },
                    ReturnValues="UPDATED_NEW"
                )
                print_color(f"Se ha vendido {action} por ${actionPrice}.", 'INFO')
            else:
                print_color("----No tiene esa acción en su portafolio para vender----", 'WARNING')
        else:
            print_color("----Acción no disponible----", 'ERROR')

