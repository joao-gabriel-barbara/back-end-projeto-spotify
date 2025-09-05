import streamlit as st
from config import BACKEND_URL
import dashboard



def show_login_page():
    
    st.set_page_config(page_title="Spotify App", layout="wide")

    # Inicializa session_state
    if "token" not in st.session_state:
        st.session_state.token = None

    # Pega token da URL
    query_params = st.experimental_get_query_params()
    token_from_url = query_params.get("token", [None])[0]

    if token_from_url and st.session_state.token is None:
        st.session_state.token = token_from_url
        st.experimental_set_query_params(token=token_from_url)
        st.experimental_rerun()  # Recarrega para mostrar dashboard

    if st.session_state.token:
        dashboard.show_dashboard()
    else:
        # ------------------- Design bonito -------------------
        st.markdown("""
    <style>                
    
    .login-container{
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center
                    }
    /* Logo com margem inferior */
    .login-container img {
        margin-bottom: 30px;
        filter: drop-shadow(0 0 2px rgba(0,0,0,0.3));
                    
    }

    /* Título */
    .login-container h1 {
        font-weight: 700;
        margin-bottom: 15px;
        font-size: 2.2rem;
    }

    /* Texto explicativo */
    .login-container p {
        font-size: 1.1rem;
        margin-bottom: 30px;
        line-height: 1.4;
    }

    /* Botão estilizado */
    .login-btn {
        display: inline-block;
        background-color: #fff;
        color: #1DB954;
        padding: 15px 50px;
        border-radius: 30px;
        text-decoration: none;
        font-weight: 700;
        font-size: 1.2rem;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        transition: background-color 0.3s ease, color 0.3s ease;
        user-select: none;
    }

    .login-btn:hover,
    .login-btn:focus {
        background-color: #e6e6e6;
        color: #17a34a;
        box-shadow: 0 6px 16px rgba(0,0,0,0.25);
    }

    /* Responsividade */
    @media (max-width: 480px) {
        .login-container {
            width: 90%;
            padding: 30px 20px;
        }
        .login-btn {
            padding: 12px 40px;
            font-size: 1rem;
        }
    }
    </style>
        """, unsafe_allow_html=True)

        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        st.image("https://storage.googleapis.com/pr-newsroom-wp/1/2018/11/Spotify_Logo_CMYK_Green.png", width=180)
        st.title("Bem-vindo ao Spotify Stats")
        st.write("Faça login com sua conta Spotify para acessar suas estatísticas.")
        login_url = f"{BACKEND_URL}/login"
        st.markdown(f'<a href="{login_url}" class="login-btn" tabindex="0">Login com Spotify</a>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
