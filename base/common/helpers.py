import os
import jwt
from datetime import datetime, timedelta


def generate_token(user_id, secret_key=None, token_version=None):

    if not secret_key:
        return {'status':0,'message': "Secret key is required for token generation"},400

    print('token_version',token_version)

    payload = {
        "id": user_id,
        "exp": datetime.utcnow() + timedelta(days=365), 'token_version': token_version
    }

    token = jwt.encode(payload, secret_key, algorithm="HS256")
    return token

def validate_schema(schema, data):
    """
    Validate given data with a Marshmallow schema.
    Returns (True, validated_data) if valid,
    or (False, error_response, status_code) if invalid.
    """
    errors = schema.validate(data)
    if errors:
        first_field = next(iter(errors))
        first_message = errors[first_field][0].lower()
        return False, {
            "status": 0,
            "message": f"{first_field} {first_message}"
        }, 400
    return True, schema.load(data), None

