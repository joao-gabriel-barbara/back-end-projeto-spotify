import streamlit as st
import requests

BACKEND_URL = "http://127.0.0.1:8000"

def show_top_tracks():
    token = st.session_state.get("token")
    if not token:
        st.warning("Faça login primeiro!")
        return

    st.title("🎵 Top Tracks")
    headers = {"Authorization": f"Bearer {token}"}

    try:
        response = requests.get(f"{BACKEND_URL}/top-tracks/me", headers=headers, timeout=10)
        response.raise_for_status()
        tracks = response.json().get("items", [])[:10]

        if tracks:
            cols = st.columns(5)
            for idx, item in enumerate(tracks):
                with cols[idx % 5]:
                    track_info = item.get("track", item)
                    album = track_info.get("album", {})
                    img_url = album.get("images", [{}])[0].get("url", "https://via.placeholder.com/160")
                    st.image(img_url, width=150)
                    duration_ms = track_info.get("duration_ms", 0)
                    minutes = duration_ms // 60000
                    seconds = (duration_ms % 60000) // 1000
                    st.caption(f"{track_info.get('name', 'Unknown')} ({minutes}:{seconds:02d})")
        else:
            st.write("Nenhuma música encontrada")
    except Exception as e:
        st.error(f"Erro ao buscar Top Tracks: {e}")
