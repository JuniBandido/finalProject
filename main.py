from app.AWSConnections import AWSConnections

aws = AWSConnections()
awsSession = aws.getSession()

def saveUserDynamoDB(session, user_data):
    dynamodb = session.resource('dynamodb')
    table = dynamodb.Table('Users_firstTable')
    response = table.put_item(Item=user_data)
    return response, print("Te has registrado con éxito! Recibiste $15,000")

email = input("Ingresa tu correo electrónico: ")
name = input("Ingrese su nombre: ")
money = 15000

user_item = {"email": email, "name": name, "money": money}

saveUserDynamoDB(awsSession, user_item)