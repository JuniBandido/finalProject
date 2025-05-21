from app.AWSConnections import AWSConnections

aws = AWSConnections()
awsSession = aws.getSession()

def saveUserDynamoDB(session, user):
  dynamodb = session.resource('dynamodb')
  table = dynamodb.Table('Users_firstTable')
  response = table.put_item(Item=user)
  return response

saveUserDynamoDB(awsSession, {"email": "local@local.com"})
print("Proceso terminado")