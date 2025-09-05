# auth.py
from fastapi import Request, HTTPException
import jwt
from datetime import datetime, timedelta, timezone
import httpx
import time
from config import client_id, client_secret, SECRET_KEY

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 dias

# ------------------- JWT -------------------

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    # Garante string em todas versões do PyJWT
    if isinstance(token, bytes):
        token = token.decode("utf-8")
    return token

def verify_access_token(token: str):
    """Verifica se o JWT é válido e retorna o usuário (sub)"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        spotify_user = payload.get("sub")
        if not spotify_user:
            raise HTTPException(status_code=401, detail="Token inválido")
        return spotify_user
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expirado")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Token inválido")

def get_user_from_request(request: Request):
    """Obtém o token do header Authorization ou do cookie"""
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
        return verify_access_token(token)
    # fallback para cookie (se quiser usar)
    token = request.cookies.get("access_token")
    if token:
        return verify_access_token(token)
    raise HTTPException(status_code=401, detail="Usuário não logado")

# ------------------- Refresh do Spotify -------------------

async def refresh_access_token(refresh_token: str):
    """Renova o access_token do Spotify usando o refresh_token"""
    body = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
        "client_id": client_id,
        "client_secret": client_secret
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://accounts.spotify.com/api/token",
            data=body,
            headers=headers
        )
        if response.status_code != 200:
            raise Exception(f"Não foi possível renovar o token: {response.text}")
        token_json = response.json()

    new_access_token = token_json["access_token"]
    expires_in = token_json.get("expires_in", 3600)  # 1 hora padrão
    new_expire = int(time.time()) + expires_in

    return new_access_token, new_expire

def verify_spotify_token(token_expiry: int) -> bool:
    """
    Retorna True se o token do Spotify ainda é válido,
    False se estiver expirado ou prestes a expirar (menos de 5 minutos)
    """
    return (token_expiry - int(time.time())) > 300
