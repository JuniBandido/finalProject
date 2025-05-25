from app.AWSConnections import AWSConnections
import boto3
from dotenv import load_dotenv
import os
import requests
from decimal import Decimal
from colorama import init, Fore, Style
import time

load_dotenv()
apiKey = os.getenv('API_KEY')
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
table = dynamodb.Table('Users_firstTable')

init(autoreset=True)
print(Fore.CYAN + Style.BRIGHT + "---- Bienvenido a INVERSIONES URL ----")

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
        intentos = 3
        while intentos > 0:
            try:
                url = f"https://api.twelvedata.com/price?symbol={symbol}&apikey={apiKey}"
                resp = requests.get(url, timeout=5).json()
                if 'price' in resp:
                    print(f"El precio actual de {name} ({symbol}) es: ${resp['price']}")
                    precios[symbol] = Decimal(resp['price'])
                    break
                else:
                    print(f"No se pudo obtener el precio de {name} ({symbol})")
                    break
            except requests.exceptions.RequestException:
                intentos -= 1
                if intentos == 0:
                    print(f"No se pudo obtener el precio de {name} ({symbol}) tras varios intentos.")
                else:
                    time.sleep(1)
    return precios

def resumenInversion():
    respuesta = table.get_item(Key={"email": usuario_id})
    usuario = respuesta.get('Item')

    if usuario:
        print(f"\n--- Resumen de Inversión de {usuario['name']} ---")
        print(f"Saldo inicial: ${usuario.get('initial_money', 'N/A')}")
        print(f"Total invertido: ${usuario.get('total_invested', 0)}")
        print(f"Saldo actual: ${usuario['money']}")

        print("\nAcciones actuales en portafolio:")
        if 'portfolio' in usuario and usuario['portfolio']:
            for accion, cantidad in usuario['portfolio'].items():
                print(f"{accion}: {cantidad}")
        else:
            print("No tienes acciones actualmente.")

        print("\nAcciones vendidas:")
        if 'sold' in usuario and usuario['sold']:
            for accion, cantidad in usuario['sold'].items():
                print(f"{accion}: {cantidad}")
        else:
            print("No has vendido acciones.")
    else:
        print("Usuario no encontrado.")

def saveUserDynamoDB(session, user_data):
    dynamodb = session.resource('dynamodb')
    table = dynamodb.Table('Users_firstTable')
    response = table.put_item(Item=user_data)
    print("Se ha registrado con éxito! Recibio $15,000")
    return response

mainmenu = input("Ingrese el número correspondiente a la acción que desea realizar\n1. - Iniciar sesión\n2. - Registrarme\n3. - Salir\n")

usuario_id = ""
money = 0

if mainmenu == "1":
    userExist = False
    while not userExist:
        usuario_id = input("Ingrese su correo: ")
        respuesta = table.get_item(Key={"email": usuario_id})
        usuario = respuesta.get('Item')
        if usuario:
            print(f"--- Bienvenido {usuario['name']}! - Tu saldo es de {usuario['money']} ---")
            money = usuario['money']
            userExist = True
        else:
            print("Usuario no encontrado.")

elif mainmenu == "2":
    aws = AWSConnections()
    awsSession = aws.getSession()
    usuario_id = input("Ingrese su correo electrónico: ")
    name = input("Ingrese su nombre: ")
    money = Decimal(15000)
    user_item = {
        "email": usuario_id,
        "name": name,
        "money": money,
        "initial_money": money,
        "total_invested": Decimal(0),
        "portfolio": {},
        "sold": {}
    }
    saveUserDynamoDB(awsSession, user_item)

elif mainmenu == "3":
    print("Gracias por visitar INVERSIONES URL")
    exit()

accion_menu = True
while accion_menu:
    WhatDo = input(f"\n¿Qué desea realizar?\n1. - Comprar acciones\n2. - Vender acciones\n3. - Ver resumen de inversión\n4. - Salir\n")

    if WhatDo == "1":
        actionsPrice = actionsList()
        action = input("¿Qué acción desea comprar? (Por favor ingrese las letras)\n").upper()

        if action in actionsPrice:
            money = Decimal(str(money))
            actionPrice = actionsPrice[action]

            respuesta = table.get_item(Key={"email": usuario_id})
            usuario = respuesta.get('Item')
            portfolio = usuario.get('portfolio', {})
            portfolio[action] = portfolio.get(action, 0) + 1
            total_invested = Decimal(usuario.get('total_invested', 0)) + actionPrice
            finalMoney = money - actionPrice

            table.update_item(
                Key={'email': usuario_id},
                UpdateExpression="SET money = :nuevo_saldo, portfolio = :portafolio, total_invested = :total",
                ExpressionAttributeValues={
                    ':nuevo_saldo': finalMoney,
                    ':portafolio': portfolio,
                    ':total': total_invested
                },
                ReturnValues="UPDATED_NEW"
            )
            print("---- Compra realizada con éxito ----")
            money = finalMoney
        else:
            print("Lo sentimos, su acción no es válida.")

    elif WhatDo == "2":
        seguir_vendiendo = True
        while seguir_vendiendo:
            actionsPrice = actionsList()
            respuesta = table.get_item(Key={"email": usuario_id})
            usuario = respuesta.get('Item')
            portfolio = usuario.get('portfolio', {})
            sold = usuario.get('sold', {})

            if not portfolio:
                print("No tienes acciones para vender.")
                break
            print("Acciones disponibles para vender:")
            for accion, cantidad in portfolio.items():
                print(f"{accion}: {cantidad}")

            action = input("¿Qué acción desea vender? (Ingresa las letras)\n").upper()
            if action in actionsPrice and portfolio.get(action, 0) > 0:
                cantidad_disponible = portfolio[action]
                cantidad_vender = input(f"Tienes {cantidad_disponible} de {action}. ¿Cuántas deseas vender?\n")
                if cantidad_vender.isdigit():
                    cantidad_vender = int(cantidad_vender)
                    if cantidad_vender <= cantidad_disponible:
                        actionPrice = actionsPrice[action]
                        money = Decimal(str(usuario['money']))
                        finalMoney = money + (actionPrice * cantidad_vender)

                        portfolio[action] -= cantidad_vender
                        if portfolio[action] == 0:
                            del portfolio[action]

                        sold[action] = sold.get(action, 0) + cantidad_vender

                        table.update_item(
                            Key={'email': usuario_id},
                            UpdateExpression="SET money = :nuevo_saldo, portfolio = :portafolio, sold = :vendidas",
                            ExpressionAttributeValues={
                                ':nuevo_saldo': finalMoney,
                                ':portafolio': portfolio,
                                ':vendidas': sold
                            },
                            ReturnValues="UPDATED_NEW"
                        )
                        print(f"Se ha vendido {cantidad_vender} de {action} por ${actionPrice * cantidad_vender}.")
                        money = finalMoney
                    else:
                        print("---- No tiene esa cantidad de acciones para vender ----")
                else:
                    print("---- Entrada inválida, ingrese un número válido ----")
            else:
                print("---- Acción no disponible o no tienes esa acción ----")

            seguir = input("\n¿Desea vender otra acción?\n1. - Sí\n2. - Volver al menú principal\n3. - Cerrar sesión\n4. - Salir del programa\n")
            if seguir != "1":
                if seguir == "2":
                    seguir_vendiendo = False
                elif seguir == "3":
                    print("Cerrando sesión...\n")
                    import sys
                    os.execl(sys.executable, sys.executable, *sys.argv)
                elif seguir == "4":
                    print("Saliendo del programa...")
                    exit()
                else:
                    print("Opción no válida. Regresando al menú principal.")
                    seguir_vendiendo = False

    elif WhatDo == "3":
        resumenInversion()
        siguiente = input("\n¿Qué desea hacer ahora?\n1. - Volver al menú principal\n2. - Cerrar sesión e ingresar otra cuenta\n3. - Salir del programa\n")
        if siguiente == "1":
            pass
        elif siguiente == "2":
            print("Cerrando sesión...\n")
            import sys
            os.execl(sys.executable, sys.executable, *sys.argv)
        elif siguiente == "3":
            print("Saliendo del programa...")
            exit()
        else:
            print("Opción no válida.")

    elif WhatDo == "4":
        print("Saliendo...")
        accion_menu = False

    else:
        print("Opción inválida.")
