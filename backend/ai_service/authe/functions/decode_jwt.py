import jwt
from jwt import PyJWTError

def decode_jwt(token: str):

    try:
        # Decode the JWT token
        decoded_token = jwt.decode(token, "your_secret_key", algorithms="HS256")
        return decoded_token['user_id']
    except PyJWTError as e:
        return "invalid"
