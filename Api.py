import requests

API_KEY = 'TU_API_KEY'  

acciones = {
    'Microsoft': 'MSFT',
    'Samsung': 'SSNLF',
    'Tesla': 'TSLA'
}

for nombre, simbolo in acciones.items():
    url = f"https://api.twelvedata.com/price?symbol={simbolo}&apikey={API_KEY}"
    respuesta = requests.get(url).json()

    if 'price' in respuesta:
        print(f"El precio actual de {nombre} ({simbolo}) es: ${respuesta['price']}")
    else:
        print(f"No se pudo obtener el precio de {nombre} ({simbolo})")

