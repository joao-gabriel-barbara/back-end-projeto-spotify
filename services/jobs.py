# jobs.py
from db import (
    insert_toptracks,
    insert_topartists,
    insert_recently_played,
    get_user_tokens,
    update_user_token,
    get_all_users
)
from auth import verify_spotify_token, refresh_access_token
import httpx
from datetime import datetime
import time

# ------------------- Coleta de dados -------------------

async def collect_top_tracks(spotify_user: str, limit=10):
    user_tokens = get_user_tokens(spotify_user)
    if not user_tokens:
        return {"error": "Usuário não encontrado"}

    access_token = user_tokens["access_token"]
    refresh_token = user_tokens["refresh_token"]
    token_expiry = user_tokens["token_expiry"]

    if not verify_spotify_token(token_expiry):
        access_token, token_expiry = await refresh_access_token(refresh_token)
        update_user_token(spotify_user, access_token, token_expiry)

    headers = {"Authorization": f"Bearer {access_token}"}

    async with httpx.AsyncClient() as client:
        response = await client.get(f"https://api.spotify.com/v1/me/top/tracks?limit={limit}&time_range=long_term", headers=headers)

    if response.status_code != 200:
        return {"error": f"Erro {response.status_code}"}

    data = response.json()
    collected_at = datetime.now().isoformat()

    for track_item in data.get("items", []):
        track = {"id": track_item["id"], "name": track_item["name"], "duration_ms": track_item["duration_ms"]}
        insert_toptracks(spotify_user, track, collected_at)

    return {"items": data.get("items", []), "collected_at": collected_at}

async def collect_top_artists(spotify_user: str, limit=10):
    user_tokens = get_user_tokens(spotify_user)
    if not user_tokens:
        return {"error": "Usuário não encontrado"}

    access_token = user_tokens["access_token"]
    refresh_token = user_tokens["refresh_token"]
    token_expiry = user_tokens["token_expiry"]

    if not verify_spotify_token(token_expiry):
        access_token, token_expiry = await refresh_access_token(refresh_token)
        update_user_token(spotify_user, access_token, token_expiry)

    headers = {"Authorization": f"Bearer {access_token}"}

    async with httpx.AsyncClient() as client:
        response = await client.get(f"https://api.spotify.com/v1/me/top/artists?limit={limit}&time_range=long_term", headers=headers)

    if response.status_code != 200:
        return {"error": f"Erro {response.status_code}"}

    data = response.json()
    collected_at = datetime.now().isoformat()

    for artist_item in data.get("items", []):
        artist = {"id": artist_item["id"], "name": artist_item["name"], "genres": artist_item["genres"], "popularity": artist_item["popularity"], "images": artist_item["images"]}
        insert_topartists(spotify_user, artist, collected_at)

    return {"items": data.get("items", []), "collected_at": collected_at}

async def collect_recently_played(spotify_user: str):
    """Coleta últimas 50 músicas recentemente reproduzidas e salva no banco."""
    user_tokens = get_user_tokens(spotify_user)
    if not user_tokens:
        print(f"Usuário {spotify_user} não encontrado")
        return {"items": [], "collected_at": None}

    access_token = user_tokens["access_token"]
    refresh_token = user_tokens["refresh_token"]
    token_expiry = user_tokens["token_expiry"]

    # Refresh automático se necessário
    if not verify_spotify_token(token_expiry):
        access_token, token_expiry = await refresh_access_token(refresh_token)
        update_user_token(spotify_user, access_token, token_expiry)

    headers = {"Authorization": f"Bearer {access_token}"}

    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://api.spotify.com/v1/me/player/recently-played?limit=50",
            headers=headers
        )

        # Se der 401, tentar refresh de token novamente
        if response.status_code == 401:
            access_token, token_expiry = await refresh_access_token(refresh_token)
            update_user_token(spotify_user, access_token, token_expiry)
            headers = {"Authorization": f"Bearer {access_token}"}
            response = await client.get(
                "https://api.spotify.com/v1/me/player/recently-played?limit=10",
                headers=headers
            )

    if response.status_code != 200:
        print(f"Erro ao buscar recentemente reproduzidas: {response.status_code}")
        return {"items": [], "collected_at": None}

    data = response.json()
    collected_at = datetime.now().isoformat()
    collected_tracks = []

    for item in data.get("items", []):
        track_info = item.get("track")
        if not track_info:
            continue  # pula se não houver track

        track = {
            "name": track_info.get("name", "Unknown"),
            "duration_ms": track_info.get("duration_ms", 0),
            "played_at": item.get("played_at")
        }
        insert_recently_played(spotify_user, track)
        collected_tracks.append(track)

    
    return {"items": collected_tracks, "collected_at": collected_at}
# ------------------- Jobs automáticos -------------------

async def refresh_tokens_job():
    """Atualiza tokens de todos os usuários que estão próximos de expirar"""
    users = get_all_users()
    for spotify_user in users:
        tokens = get_user_tokens(spotify_user)
        if not tokens:
            continue
        if tokens["token_expiry"] - int(time.time()) < 300:
            new_access_token, new_expiry = await refresh_access_token(tokens["refresh_token"])
            update_user_token(spotify_user, new_access_token, new_expiry)
            

async def run_for_all_users(collect_function):
    """Executa uma coleta (top tracks, top artists ou recently played) para todos os usuários"""
    users = get_all_users()
    for spotify_user in users:
        await collect_function(spotify_user)
