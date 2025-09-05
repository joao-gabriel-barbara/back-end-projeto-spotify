import streamlit as st
import requests
from datetime import datetime

BACKEND_URL = "http://127.0.0.1:8000"

def show_recently_played():
    token = st.session_state.get("token")
    if not token:
        st.warning("Faça login primeiro!")
        return

    st.title("⏱️ Recently Played")
    headers = {"Authorization": f"Bearer {token}"}

    num_tracks = st.slider("Número de músicas a exibir:", min_value=5, max_value=50, value=10, step=5)

    try:
        response = requests.get(f"{BACKEND_URL}/recently-played/me", headers=headers, timeout=10)
        response.raise_for_status()
        recent_tracks = response.json().get("items", [])[:num_tracks]  

        if recent_tracks:
            # Agrupa em blocos de 5
            for i in range(0, len(recent_tracks), 5):
                row_tracks = recent_tracks[i:i+5]
                cols = st.columns(len(row_tracks))
                for idx, item in enumerate(row_tracks):
                    track_info = item.get("track", item)
                    played_at = item.get("played_at", "")
                    played_time = ""
                    if played_at:
                        dt = datetime.fromisoformat(played_at.replace("Z", "+00:00"))
                        played_time = dt.strftime('%d/%m %H:%M')

                    # Nome do artista
                    artists = track_info.get("artists", [])
                    artist_names = ", ".join([artist.get("name", "Unknown") for artist in artists])

                    # Duração
                    duration_ms = track_info.get("duration_ms", 0)
                    minutes = duration_ms // 60000
                    seconds = (duration_ms % 60000) // 1000

                    # Conteúdo do card
                    card_html = f"""
                    <div style="
                        background-color: #121212; 
                        padding: 12px; 
                        border-radius: 12px; 
                        text-align: center;
                        box-shadow: 0 2px 6px rgba(0,0,0,0.5);
                        color: white;
                        margin-bottom: 10px;
                    ">
                        <div style="font-weight:bold; font-size:14px;">{track_info.get('name', 'Unknown')}</div>
                        <div style="font-size:12px; color:#b3b3b3;">{artist_names}</div>
                        <div style="font-size:11px; color:#999;">⏱ {minutes}:{seconds:02d}<br>📅 {played_time}</div>
                    </div>
                    """
                    cols[idx].markdown(card_html, unsafe_allow_html=True)
        else:
            st.info("Nenhuma música recentemente reproduzida")
    except Exception as e:
        st.error(f"Erro ao buscar Recently Played: {e}")
