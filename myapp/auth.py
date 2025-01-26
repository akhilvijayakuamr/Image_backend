from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.exceptions import PermissionDenied



# Get id form token

def get_user_from_token(token):
    try:
        validated_token = JWTAuthentication().get_validated_token(token)
        user_id = validated_token["user_id"]
        return user_id
    except (AuthenticationFailed, InvalidToken) as e:
        raise InvalidToken("Invalid or expired token.")
    
    
  
# Get token from request

def get_token_from_request(request):
    auth_header = request.headers.get('Authorization')
    if auth_header and auth_header.startswith('Bearer '):
        return auth_header[7:]
    else:
        raise PermissionDenied('Token is missing or invalid format.')