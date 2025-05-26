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

main_menu = input(Fore.YELLOW + "Ingrese el numero correspondiente a la acción que desea realizar\n1. - Iniciar sesion\n2. - Registrarme\n3. - Salir\n")

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

def actions_list():
    actions = {
        'Microsoft': 'MSFT',
        'Samsung': 'SSNLF',
        'Tesla': 'TSLA',
        'Nvidia': 'NVDA',
        'Toyota': 'TM'
    }

    prices = {}

    for name, symbol in actions.items():
        attempts = 3
        while attempts > 0:
            try:
                url = f"https://api.twelvedata.com/price?symbol={symbol}&apikey={apiKey}" # api url de precios
                resp = requests.get(url, timeout=5)
                data = resp.json()
                if 'price' in data and data['price'] not in [None, 'None', '', 'null']:
                    print_color(f"[INFO] Precio actual de {name} ({symbol}): ${data['price']}", 'INFO') # precios obtenidos 
                    prices[symbol] = Decimal(data['price'])
                    attempts = 0
                else:
                    error_msg = data.get('message', 'Respuesta inválida.')
                    print_color(f"[ERROR] No se pudo obtener el precio de {name} ({symbol}): {error_msg}", 'ERROR')
                    attempts = 0
            except Exception as e:
                attempts -= 1
                if attempts == 0:
                    print_color(f"[ERROR] No se pudo obtener el precio de {name} ({symbol}) tras varios intentos.", 'ERROR')
                else:
                    time.sleep(4)
        time.sleep(4) # tiempo de espera entre cada acción
    return prices

def new_money():
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('Users_firstTable')
    response = table.update_item(
        Key={'email': user_id}, # clave primaria del email
        UpdateExpression="SET money = :new_balance", # actializa el saldo
        ExpressionAttributeValues={':new_balance': final_money},
        ReturnValues="UPDATED_NEW"
    )

    print_color(Fore.MAGENTA + "---- Saldo actualizado ----", 'INFO')
    print_color(f"Nuevo saldo: {response['Attributes']['money']}", 'INFO')

resp = actions_list

if main_menu == "1":
    user_exists = False
    while user_exists == False:
        load_dotenv()
        "aws_access_key_id" == os.getenv("aws_access_key_id")
        "aws_secret_access_key" == os.getenv("aws_secret_access_key")
        
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        table = dynamodb.Table('Users_firstTable')

        user_id = input("Ingrese su correo: ") # pide el email
        response = table.get_item(Key={"email": user_id})
        user = response.get('Item')

        if user:
            print_color("Usuario encontrado:", 'INFO')
            print_color(Fore.CYAN + f"--- Bienvenido {user['name']}! - Tu saldo es de {user['money']} ---", 'INFO')
            money = user['money'] # muestra el saldo actual
            user_exists = True
        else:
            print_color("Usuario no encontrado.", 'ERROR')

elif main_menu == "2":
    aws = AWSConnections()
    aws_session = aws.getSession()

    def save_user_dynamodb(session, user_data):
        dynamodb = session.resource('dynamodb')
        table = dynamodb.Table('Users_firstTable')
        response = table.put_item(Item=user_data)

        print_color("Se ha registrado con éxito! Recibio $15,000", 'INFO')
        return response, table

    email = user_id = input("Ingrese su correo electrónico: ")
    name = input("Ingrese su nombre: ")
    money = 15000
    user_item = {"email": email, "name": name, "money": money}

    save_user_dynamodb(aws_session, user_item)

elif main_menu == "3":
    print_color("Gracias por vicitar inverisones URL", 'INFO')
    exit()

program_running = True
while program_running == True:

    what_do = input(Fore.MAGENTA + f"Que desea realizar?\n1. - Comprar acciones\n2. - Vender acciones\n3. - Ver resumen de inversión\n4. - Salir\n")
    if what_do == "1":
        actions_price = actions_list()
        action = input(Fore.LIGHTCYAN_EX + "¿Qué acción desea comprar? (Por favor ingrese las letras)\n").upper()

        if action in actions_price:
            money = Decimal(str(money))
            action_price = actions_price[action]
            final_money = money - action_price   # actualiza el saldo despues de la compra

            response = table.get_item(Key={"email": user_id})
            user = response.get('Item')
            portfolio = user.get('portfolio', {})
            history = user.get('history', [])

            if action in portfolio:
                portfolio[action] += 1
            else:
                portfolio[action] = 1

            timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            history.append({
                "type": "compra",
                "accion": action,
                "precio": str(action_price),
                "fecha": timestamp
            })

            table.update_item(
                Key={'email': user_id},
                UpdateExpression="SET money = :new_balance, portfolio = :portfolio, history = :history",
                ExpressionAttributeValues={
                    ':new_balance': final_money,
                    ':portfolio': portfolio,
                    ':history': history
                },
                ReturnValues="UPDATED_NEW"
            )
            print_color(f"----Compra realizada con éxito----", 'INFO')
            new_money()

        else:
            print_color("Lo sentimos su acción no es válida.", 'ERROR')

    elif what_do == "2":
        actions_price = actions_list()

        response = table.get_item(Key={"email": user_id})
        user = response.get('Item')
        portfolio = user.get('portfolio', {})
        history = user.get('history', [])

        if portfolio:
            print_color("Acciones disponibles para vender:", 'INFO')
            for accion, cantidad in portfolio.items():
                print_color(f"{accion}: {cantidad}", 'NORMAL')
        else:
            print_color("No tienes acciones para vender.", 'WARNING')

        action = input("¿Qué acción desea vender? (Ingresa las letras)\n").upper()

        if action in actions_price:
            investment = Decimal(str(user.get('investment', 0)))
            action_price = actions_price[action]
            money = Decimal(str(user['money']))

            if portfolio.get(action, 0) > 0:
                final_money = money + action_price
                portfolio[action] -= 1
                if portfolio[action] == 0:
                    del portfolio[action]
                timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                history.append({
                    "type": "venta",
                    "accion": action,
                    "precio": str(action_price),
                    "fecha": timestamp
                })

                table.update_item(
                    Key={'email': user_id},
                    UpdateExpression="SET money = :new_balance, portfolio = :portfolio, history = :history REMOVE investment",
                    ExpressionAttributeValues={
                        ':new_balance': final_money,
                        ':portfolio': portfolio,
                        ':history': history
                    },
                    ReturnValues="UPDATED_NEW"
                )
                print_color(f"Se ha vendido {action} por ${action_price}.", 'INFO')
            else:
                print_color("----No tiene esa acción en su portafolio para vender----", 'WARNING')
        else:
            print_color("----Acción no disponible----", 'ERROR')

    elif what_do == "3":
        def investment_summary():
            response = table.get_item(Key={"email": user_id})
            user = response.get('Item')

            if user:
                print_color(Fore.CYAN + f"---Resumen de Inversión de {user['name']} ---", 'INFO')
                portfolio = user.get('portfolio', {})
                if portfolio:
                    print_color("Acciones en las que ha invertido:", 'INFO')
                    for accion, cantidad in portfolio.items():
                        print_color(f"{accion}: {cantidad}", 'NORMAL')
                else:
                    print_color("Aún no ha invertido en ninguna acción.", 'WARNING')
                print_color(f"Saldo disponible: ${user['money']}", 'INFO')
                history = user.get('history', [])
                if history:
                    print_color("\nHistorial de transacciones:", 'INFO')
                    for evento in history:
                        precio = evento.get('precio', 'N/A')
                        print_color(f"- {evento['fecha']} | {evento['type'].capitalize()} | Acción: {evento['accion']} | Precio: ${precio}", 'NORMAL')
                else:
                    print_color("No hay historial de transacciones.", 'WARNING')
            else:
                print_color("Usuario no encontrado.", 'ERROR')
        investment_summary()
    elif what_do == "4":
        print_color("Saliendo...", 'INFO')
        exit()
