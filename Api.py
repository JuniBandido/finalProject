import requests
from dotenv import load_dotenv  #se importa dotenv para leer el .env
import os   #para sacar algo de .env

load_dotenv()   #se carga el acrhivo .env

apiKey = os.getenv('API_KEY')   #se saca la key de la api

def actionsList():
    actions = {
        'Microsoft': 'MSFT',
        'Samsung': 'SSNLF',
        'Tesla': 'TSLA',
        'Nvidia': 'NVDA',
        'Toyota': 'TYO'
    }

    for name, symbol in actions.items():
        url = f"https://api.twelvedata.com/price?symbol={symbol}&apikey={apiKey}"
        resp = requests.get(url).json()

        if 'price' in resp:
            print(f"El precio actual de {name} ({symbol}) es: ${resp['price']}")
        else:
            print(f"No se pudo obtener el precio de {name} ({symbol})")

actionsList()