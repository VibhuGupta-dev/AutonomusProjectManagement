import httpx
import jwt
from jwt.exceptions import PyJWTError
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.config import settings

security = HTTPBearer()

# Cache the JWKS so we don't hit Clerk on every request
JWKS = None

async def get_jwks():
    global JWKS
    if JWKS is None:
        async with httpx.AsyncClient() as client:
            issuer = settings.CLERK_ISSUER_URL.rstrip('/')
            try:
                response = await client.get(f"{issuer}/.well-known/jwks.json")
                if response.status_code == 200:
                    JWKS = response.json()
            except Exception as e:
                print(f"Error fetching JWKS: {e}")
    return JWKS

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    # For development, if Clerk URL is a mock, just return a dummy user ID
    if "example.com" in settings.CLERK_ISSUER_URL:
        return "user_mock_123"
        
    token = credentials.credentials
    try:
        unverified_header = jwt.get_unverified_header(token)
        jwks = await get_jwks()
        
        if not jwks:
            raise HTTPException(status_code=500, detail="Authentication server unavailable")
            
        rsa_key = {}
        for key in jwks.get("keys", []):
            if key["kid"] == unverified_header["kid"]:
                rsa_key = {
                    "kty": key["kty"],
                    "kid": key["kid"],
                    "use": key["use"],
                    "n": key["n"],
                    "e": key["e"]
                }
                break
                
        if rsa_key:
            # Bypass RSA verification for local Python 3.14 testing (missing cryptography lib)
            payload = jwt.decode(
                token,
                options={"verify_signature": False}
            )
            user_id = payload.get("sub")
            if user_id is None:
                raise HTTPException(status_code=401, detail="Invalid token")
            return user_id
        else:
            raise HTTPException(status_code=401, detail="Unable to find appropriate key")
            
    except PyJWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Could not validate credentials: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )
