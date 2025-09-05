# main.py
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from datetime import timedelta, timezone, datetime
import httpx
import time
import sqlite3
from config import client_id, client_secret, redirect_uri, scope, SECRET_KEY, frontend_url
from auth import create_access_token, get_user_from_request
from jobs import collect_recently_played, collect_top_artists, collect_top_tracks, run_for_all_users, refresh_tokens_job
from scheduler import start_scheduler, scheduler
from db import insert_user, get_user_tokens

# ------------------- Lifespan -------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    start_scheduler()
    print("Scheduler iniciado ✅")
    yield
    scheduler.shutdown()
    print("Scheduler finalizado ✅")

app = FastAPI(title="Spotify Stats API", version="1.0.0", lifespan=lifespan)

# ------------------- CORS -------------------
  # Streamlit
app.add_middleware(
    CORSMiddleware,
    allow_origins=[frontend_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------- Rotas -------------------

@app.get("/login")
async def login():
    """Redireciona para autorização do Spotify"""
    import urllib.parse
    auth_url = "https://accounts.spotify.com/authorize?" + urllib.parse.urlencode({
        "client_id": client_id,
        "response_type": "code",
        "redirect_uri": redirect_uri,
        "scope": scope
    })
    return RedirectResponse(auth_url)

@app.get("/callback")
async def callback(request: Request):
    """Callback do Spotify: troca código por token, salva no DB e retorna JWT"""
    code = request.query_params.get("code")
    if not code:
        return RedirectResponse(f"{frontend_url}/?error=sem_codigo")

    # Troca código por token
    body = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": redirect_uri,
        "client_id": client_id,
        "client_secret": client_secret
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    async with httpx.AsyncClient() as client:
        response = await client.post("https://accounts.spotify.com/api/token", data=body, headers=headers)
        token_json = response.json()

    if response.status_code != 200:
        return RedirectResponse(f"{frontend_url}/?error=token_failed")

    access_token = token_json["access_token"]
    refresh_token = token_json["refresh_token"]
    expires_in = token_json["expires_in"]
    token_expiry = int(time.time()) + expires_in

    # Pega perfil do usuário
    async with httpx.AsyncClient() as client:
        user_profile = await client.get(
            "https://api.spotify.com/v1/me",
            headers={"Authorization": f"Bearer {access_token}"}
        )
    profile_json = user_profile.json()
    spotify_user_id = profile_json.get("id")
    if not spotify_user_id:
        return RedirectResponse(f"{frontend_url}/?error=profile_failed")

    # Salva usuário no DB
    insert_user(
        spotify_user=spotify_user_id,
        access_token=access_token,
        refresh_token=refresh_token,
        token_expiry=token_expiry
    )

    # Cria JWT para frontend
    token = create_access_token({"sub": spotify_user_id}, expires_delta=timedelta(seconds=expires_in))
    return RedirectResponse(f"{frontend_url}/?token={token}")

# ------------------- Endpoints protegidos -------------------

@app.get("/me")
async def me(request: Request):
    spotify_user = get_user_from_request(request)
    return {"spotify_user": spotify_user}

@app.get("/top-artists/me")
async def top_artists_me(request: Request):
    spotify_user = get_user_from_request(request)
    return await collect_top_artists(spotify_user)

@app.get("/top-tracks/me")
async def top_tracks_me(request: Request):
    spotify_user = get_user_from_request(request)
    return await collect_top_tracks(spotify_user)

@app.get("/recently-played/me")
async def recently_played_me(request: Request):
    spotify_user = get_user_from_request(request)
    return await collect_recently_played(spotify_user)

@app.get("/track-count")
async def track_count(request: Request):
    spotify_user = get_user_from_request(request)  # pega usuário do token
    result = await collect_recently_played(spotify_user)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result

@app.get("/stats/me")
async def user_stats(request: Request):
    spotify_user = get_user_from_request(request)

    conn = sqlite3.connect("spotify_data.db")
    cursor = conn.cursor()

    now = datetime.now(timezone.utc)

    # Busca todas as músicas do usuário
    cursor.execute(
        "SELECT played_at, duration_ms FROM recently_played WHERE spotify_user_id = ?",
        (spotify_user,)
    )
    rows = cursor.fetchall()
    conn.close()

    # Processa
    total = len(rows)
    total_24h = 0
    total_7d = 0
    minutes_24h = 0
    minutes_7d = 0
    minutes_total = 0

    for played_at, duration_ms in rows:
        played_time = datetime.fromisoformat(played_at.replace("Z", "+00:00"))

        if played_time > now - timedelta(days=1):
            total_24h += 1
            minutes_24h += duration_ms // 60000
        if played_time > now - timedelta(days=7):
            total_7d += 1
            minutes_7d += duration_ms // 60000

    return {
        "total_24h": total_24h,
        "total_7d": total_7d,
        "total": total,
        "minutes_24h": minutes_24h,
        "minutes_7d": minutes_7d,
        "minutes_total" : minutes_total
    }


# ------------------- Job manual -------------------

@app.get("/refresh-tokens")
async def refresh_tokens():
    await refresh_tokens_job()
    return {"msg": "Tokens atualizados para todos os usuários"}
