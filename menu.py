import time

CLIENTES = {
    5677804: {"nombre": "Eduardo orellana", "correo": "Eduardoorll58@gmail.com", "saldo": 15000.00},
    1083445: {"nombre": "Jose Nolberto", "correo": "Nolbretose885@gmail.com", "saldo": 15000.00},
    30999834: {"nombre": "Ruiz Alberto", "correo": "Rujberto285@gmail.com", "saldo": 15000.00}
}
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
