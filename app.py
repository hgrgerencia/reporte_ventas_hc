import streamlit as st
from page.dashboard import vista_dashboard
from page.sell_in import vista_sell_in
from page.coordinadores import vista_corrdinadores
from page.distribuidoras import vista_distribuidoras
from page.coord_chocolates import vista_corrdinadores_chocolates
from page.dist_chocolates import vista_distribuidoras_chocolates

def local_css():
    # Configuración de la página
    st.set_page_config(page_title="Inciar Sesión", page_icon="📊", layout="centered")

    st.markdown("""
    <style>
    /* Ocultar barra de Deploy, menú de hamburguesa y pie de página de Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display:none;}

    /* Fondo con gradiente más vívido y saturado */
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }

    /* Contenedor del Login mejorado */
    [data-testid="stVerticalBlock"] > div:has(div.login-card) {
        background-color: rgba(255, 255, 255, 0.95);
        padding: 50px;
        border-radius: 20px;
        box-shadow: 0 20px 40px rgba(0,0,0,0.2);
    }

    /* Estilo del título con color vibrante */
    .main-title {
        font-family: 'Inter', sans-serif;
        color: #1e3a8a;
        text-align: center;
        font-weight: 800;
        margin-bottom: 30px;
        letter-spacing: -1px;
    }

    /* Estilo de los inputs con bordes más definidos */
    .stTextInput > div > div > input {
        border-radius: 10px;
        border: 2px solid #e2e8f0;
        padding: 12px;
        font-size: 16px;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.2);
    }

    /* Botón con color púrpura/azul intenso y gradiente */
    div.stButton > button {
        width: 100%;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        font-weight: bold;
        border-radius: 10px;
        border: none;
        padding: 15px;
        font-size: 18px;
        transition: all 0.3s ease;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    div.stButton > button:hover {
        background: linear-gradient(90deg, #764ba2 0%, #667eea 100%);
        color: white;
        transform: scale(1.02);
        box-shadow: 0 5px 15px rgba(118, 75, 162, 0.4);
    }

    /* Estilo para los enlaces del pie */
    .footer-text {
        text-align: center;
        font-size: 0.9rem;
        color: #4a5568;
        margin-top: 25px;
    }
    
    .footer-text a {
        color: #764ba2;
        text-decoration: none;
        font-weight: 600;
    }
    
    .footer-text a:hover {
        text-decoration: underline;
    }
    </style>
    """, unsafe_allow_html=True)

def show_login():
    local_css()


    # Logo con un color que resalte
    st.markdown("<h1 style='text-align: center; color: white; font-size: 80px; margin-bottom: 0;'>🔑</h1>", unsafe_allow_html=True)
    st.markdown("<h2 class='main-title'>Iniciar Sesión</h2>", unsafe_allow_html=True)
    
    with st.container():
        username = st.text_input("Usuario o Correo", placeholder="Ingresa tu usuario")
        password = st.text_input("Contraseña", type="password", placeholder="••••••••")
        
        col_c, col_r = st.columns([1, 1])
        with col_c:
            st.checkbox("Recordarme")
        

        if st.button("Entrar al Portal", use_container_width=True):
            if username == "admin" and password == "1234":
                st.session_state.logged_in = True
                st.session_state.user = "Admin Pro"
                st.rerun()
            else:
                st.error("Error: Usuario o contraseña no válidos.")

def dashboard_css():
    st.set_page_config(page_title="Análisis de Datos", page_icon="📊", layout="wide")

    st.markdown("""
    <style>
    .block-container { padding-top: 3rem; }
    /* 2. ESTILOS GLOBALES */
    .stApp {
        background-color: #f8fafc;
    }

    /* 3. ESTILOS DEL LOGIN (Degradado Original Vívido) */
    .login-bg {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        position: fixed;
        top: 0; left: 0; width: 100vw; height: 100vh;
        z-index: -1;
    }

    .login-card-container {
        background-color: white;
        padding: 40px;
        border-radius: 15px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.3);
        max-width: 400px;
        margin: auto;
    }

    /* Título del Login */
    .login-title {
        color: #2c3e50;
        text-align: center;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        font-weight: 700;
        margin-bottom: 10px;
    }

    /* Botón de login estilo original */
    div.stButton > button {
        width: 100%;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        font-weight: bold !important;
        border-radius: 8px !important;
        border: none !important;
        padding: 12px !important;
        transition: all 0.3s ease !important;
    }

    div.stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
    }

    /* 4. ESTILOS DEL DASHBOARD */
    .top-bar {
        background-color: white;
        padding: 1rem 2rem;
        border-radius: 10px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        border: 1px solid #e2e8f0;
        margin-bottom: 2rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
    }
    
    .metric-card {
        background-color: white;
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.03);
    }

    /* Sidebar Profesional */
    [data-testid="stSidebar"] {
        background-color: #1e293b !important;
    }
    [data-testid="stSidebar"] * {
        color: #f8fafc !important;
    }
    </style>
    """, unsafe_allow_html=True)
def show_dashboard():
    dashboard_css()
    # Barra Lateral
    with st.sidebar:
        st.markdown("## 📊 PRO PANEL")
        st.write("---")
        menu = st.radio("Helados", ["📊 Dashboard", "📦 SELL IN", "Coordinadores", "Distribuidoras", "Coord. Chocolates", "Dist. Chololates"])

        st.write("---")
        if st.button("Cerrar Sesión", use_container_width=True):
            st.session_state.logged_in = False
            st.rerun()
        
    # Barra Superior
    st.markdown(f"""
        <div class="top-bar">
            <div style="font-weight: 700; color: #1e293b; font-size: 1.1rem;">{menu}</div>
            <div style="display: flex; align-items: center; gap: 20px;">
                <span style="font-size: 0.85rem; color: #64748b;">Estado: <b style="color: #10b981;">Activo</b></span>
                <span style="font-weight: 600; color: #1e293b;">{st.session_state.user}</span>
                <div style="width: 35px; height: 35px; background: #667eea; border-radius: 50%; display: flex; justify-content: center; align-items: center; color: white;">A</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    if menu == "📊 Dashboard":
        vista_dashboard()
    elif menu == "📦 SELL IN":
        vista_sell_in()
    elif menu == "Coordinadores":
        vista_corrdinadores()
    elif menu == "Distribuidoras":
        vista_distribuidoras()
    elif menu == "Coord. Chocolates":
        vista_corrdinadores_chocolates()
    elif menu == "Dist. Chololates":
        vista_distribuidoras_chocolates()





# Lógica de Inicio
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    show_login()
else:
    show_dashboard()