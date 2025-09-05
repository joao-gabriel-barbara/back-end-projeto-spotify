# dashboard.py
import streamlit as st
import requests
from datetime import datetime, timedelta, timezone
from pages_module import top_artists as ta, top_tracks as tt, recently_played as rp
from streamlit_autorefresh import st_autorefresh

BACKEND_URL = "http://127.0.0.1:8000"  # ou seu backend em deploy

def get_headers():
    token = st.session_state.token
    return {"Authorization": f"Bearer {token}"}

def show_dashboard():
    st.title("🎵 Spotify Dashboard")

    # Auto refresh a cada 5 minutos (300000 ms)
    st_autorefresh(interval=300000, key="dashboard_autorefresh")

    # Sidebar com seções
    page = st.sidebar.radio("Seções", ["Resumo", "Top Artists", "Top Tracks", "Recently Played"])

    if page == "Resumo":
        show_summary()
    elif page == "Top Artists":
        ta.show_top_artists()
    elif page == "Top Tracks":
        tt.show_top_tracks()
    elif page == "Recently Played":
        rp.show_recently_played()

def show_summary():
    st.subheader("Resumo do usuário")

    token = st.session_state.token
    headers = {"Authorization": f"Bearer {token}"}

    try:
        response = requests.get(f"{BACKEND_URL}/stats/me", headers=headers, timeout=10)
        if response.status_code == 401:
            st.error("Token expirado ou inválido. Faça login novamente.")
            st.stop()

        stats = response.json()

        # ------------------- Estatísticas principais em "cards" -------------------
        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("Músicas tocadas (24h)", stats.get("total_24h", 0))
        col2.metric("Músicas tocadas (7 dias)", stats.get("total_7d", 0))
        col3.metric("Total de músicas", stats.get("total", 0))
        col4.metric("Minutos tocados (24h)", stats.get("minutes_24h", 0))
        col5.metric("Minutos tocados (7 dias)", stats.get("minutes_7d", 0))

        st.markdown("---")
        st.info("Use a barra lateral para navegar nas abas de detalhes.")

    except Exception as e:
        st.error(f"Erro ao buscar estatísticas: {e}")


