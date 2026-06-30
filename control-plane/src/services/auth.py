from fastapi import HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from database.connection import load_config

security = HTTPBearer()

def get_api_token() -> str:
    config = load_config()
    return config.get("api_token", "token_cerynix_secret_key_2026")

def verify_token(credentials: HTTPAuthorizationCredentials = Security(security)) -> str:
    token = credentials.credentials
    expected_token = get_api_token()
    if token != expected_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API Bearer Token"
        )
    return token
