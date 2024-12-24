import jwt
import datetime

SECRET_KEY = '12345'  
def generate_jwt_token(username):
    
    expiration = datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    
 
    payload = {
        'username': username,
        'exp': expiration
    }
  
    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    return token
def decode_jwt_token(token):
    try:
      
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return 'Token has expired'
    except jwt.InvalidTokenError:
        return 'Invalid token'
