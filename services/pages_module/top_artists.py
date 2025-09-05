import streamlit as st
import requests

BACKEND_URL = "http://127.0.0.1:8000"

def show_top_artists():
    token = st.session_state.get("token")
    if not token:
        st.warning("Faça login primeiro!")
        return

    st.title("🎤 Top Artists")
    headers = {"Authorization": f"Bearer {token}"}

    try:
        response = requests.get(f"{BACKEND_URL}/top-artists/me", headers=headers, timeout=10)
        response.raise_for_status()
        artists = response.json().get("items", [])[:10]

        if artists:
            cols = st.columns(5)
            for idx, item in enumerate(artists):
                with cols[idx % 5]:
                    img_url = item["images"][0]["url"] if item.get("images") else "https://via.placeholder.com/160"
                    st.image(img_url, width=150)
                    st.caption(item["name"])
        else:
            st.write("Nenhum artista encontrado")
    except Exception as e:
        st.error(f"Erro ao buscar Top Artists: {e}")
