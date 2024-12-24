import jwt
import datetime

# Секретный ключ для подписи токена
SECRET_KEY = 'your_secret_key'  # Замените на свой секретный ключ

# Функция для генерации JWT токена
def generate_jwt_token(username):
    # Устанавливаем время истечения токена (например, 1 час)
    expiration = datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    
    # Создаем payload (данные, которые будут закодированы в токене)
    payload = {
        'username': username,
        'exp': expiration
    }
    
    # Генерируем токен
    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    return token

# Функция для декодирования JWT токена
def decode_jwt_token(token):
    try:
        # Декодируем токен
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return 'Token has expired'
    except jwt.InvalidTokenError:
        return 'Invalid token'

# Пример использования
if __name__ == '__main__':
    username = 'testuser'
    
    # Генерация токена
    token = generate_jwt_token(username)
    print(f'Generated JWT Token: {token}')
    
    # Декодирование токена
    decoded_payload = decode_jwt_token(token)
    print(f'Decoded Payload: {decoded_payload}')