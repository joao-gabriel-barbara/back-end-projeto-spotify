import streamlit as st
import login, dashboard
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

st.set_page_config(page_title="Spotify Stats", layout="wide")

# Inicializa session_state
if "token" not in st.session_state:
    st.session_state.token = None

# Pega token da URL (callback)
query_params = st.experimental_get_query_params()
token_from_url = query_params.get("token", [None])[0]

if token_from_url and st.session_state.token is None:
    st.session_state.token = token_from_url
    st.experimental_set_query_params(token=token_from_url)

# Se houver token, vai para dashboard completo com sidebar
if st.session_state.token:
    dashboard.show_dashboard()  # <== aqui, chama show_dashboard()
else:
    login.show_login_page()