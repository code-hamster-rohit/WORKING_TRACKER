import os
from google.oauth2 import id_token
from google.auth.transport import requests

def decode_token(token):
    try:
        decoded_token = id_token.verify_oauth2_token(
            token,
            requests.Request(),
            os.environ.get('GOOGLE_CLIENT_ID')
        )
        return decoded_token
    except Exception:
        return None

def extract_info(decoded_token, expected_claims):
    try:
        if not decoded_token:
            return None
        return {
            claim: decoded_token.get(claim) 
            for claim in expected_claims
        }
    except Exception:
        return None