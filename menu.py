from dotenv import load_dotenv
import boto3
import os

def Login(): #Funcion para iniciar sesion
    userExist = False
    while userExist == False:
        load_dotenv()
        "aws_access_key_id" == os.getenv("aws_access_key_id")
        "aws_secret_access_key" == os.getenv("aws_secret_access_key")
        
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')

        tabla = dynamodb.Table('Users_firstTable')

        usuario_id = input("Ingresa tu correo: ")

        respuesta = tabla.get_item(Key={"email": usuario_id})

        usuario = respuesta.get('Item')

        if usuario:
            print("✅ Usuario encontrado:")
            print(f"Bienvenido {usuario['name']}!")
            userExist = True
        else:
            print("❌ Usuario no encontrado.")


        

"""""
CLIENTES = usuario

def buscar_usuario(nombre):
    for id_unico, datos in CLIENTES.items():
        if datos["nombre"].lower() == nombre.lower():
            return id_unico, datos
    return None, None

def menu_usuario(id_usuario, cliente):
    print(f"\n Bienvenido {cliente['nombre']}")
    ejecutando = True
    while ejecutando:
        print(f"Saldo actual: ${cliente['saldo']:.2f}")
        print("\n---// MENÚ DE USUARIO //---")
        print("1. Ver información del usuario")
        print("2. Ver ID único")
        print("3. Salir")

        opcion = input("Seleccione una opción: ")

        if opcion == "1":
            print(f"\n Usuario: {cliente['nombre']}")
            print(f" Correo: {cliente['correo']}")
        elif opcion == "2":
            print(f"\n Su ID único es: {id_usuario}")
        elif opcion == "3":
            print("\n Saliendo del usuario...\n")
            time.sleep(0)
            ejecutando = False
        else:
            print(" X Opción no válida, por favor intente de nuevo.")
def main():
    print("\n ==//= Sistema de Clientes =//==")
    ejecutando = True
    while ejecutando:
        nombre = input("\n Ingrese su nombre o 'salir' para salir del menu: ")
        if nombre.lower() == "salir":
            print("Gracias por visitarnos en HNT la plataforma de inversion en criptomonedas")
            ejecutando = False
        else:
            id_usuario, cliente = buscar_usuario(nombre)
            if cliente:
                menu_usuario(id_usuario, cliente)
            else:
                print(" X Usuario no encontrado, por favir intente nuevamente.")

main()
"""""