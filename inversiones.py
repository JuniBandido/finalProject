import boto3
from decimal import Decimal
from datetime import datetime

dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
tabla_usuarios = dynamodb.Table('proyecto')       
tabla_inversiones = dynamodb.Table('Inversiones') 

def realizar_inversion(user_id, nombre_accion, monto_invertido):
    usuario = tabla_usuarios.get_item(Key={'users': user_id})

    if 'Item' not in usuario:
        return {"error": "Usuario no encontrado"}

    saldo_actual = Decimal(str(usuario['Item']['saldo']))  

    if saldo_actual < monto_invertido:
        return {"error": "Saldo insuficiente"}

    inversion = {
        'inversion_id': f"{user_id}_{datetime.now().isoformat()}",
        'user_id': user_id,
        'accion': nombre_accion,
        'monto': float(monto_invertido),
        'fecha': datetime.now().isoformat()
    }

    tabla_inversiones.put_item(Item=inversion)

    nuevo_saldo = saldo_actual - monto_invertido

    tabla_usuarios.update_item(
        Key={'users': user_id},
        UpdateExpression='SET saldo = :nuevo',
        ExpressionAttributeValues={':nuevo': nuevo_saldo}
    )

    return {
        "mensaje": "Inversión realizada con éxito",
        "nuevo_saldo": float(nuevo_saldo)
}