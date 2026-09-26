import streamlit as st
import pandas as pd

# -----------------------------------------
# KONFIGURACJA STRONY I WYGLĄDU
# -----------------------------------------
st.set_page_config(page_title="Kalkulator Heli", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; color: #000000; }
    .css-1d391kg { background-color: #111111; } 
    .stButton>button { background-color: #CC0000; color: white; border-radius: 5px; border: none; font-weight: bold; }
    .stButton>button:hover { background-color: #990000; color: white; }
    h1, h2, h3 { color: #CC0000; font-family: 'Arial', sans-serif; }
    .price-box { padding: 20px; background-color: #f8f9fa; border-left: 5px solid #CC0000; font-size: 24px; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# -----------------------------------------
# FUNKCJA WCZYTYWANIA PRAWDZIWEJ BAZY DANYCH
# -----------------------------------------
@st.cache_data
def load_data():
    file_name = "KONFIGURATOR CEN TRUCK MOTOR 14.09.2026 (spalinowe i elektryczne wózki czołowe).xlsm"
    try:
        # Wczytujemy zakładkę Baza_Wozki
        df_wozki = pd.read_excel(file_name, sheet_name="Baza_Wozki", engine="openpyxl")
        return df_wozki
    except Exception as e:
        return None

# -----------------------------------------
# BAZA UŻYTKOWNIKÓW 
# -----------------------------------------
if 'users_db' not in st.session_state:
    st.session_state.users_db = {
        "admin": {"password": "123", "role": "Administrator", "name": "Szefowa"},
        "kierownik": {"password": "123", "role": "Menedżer", "name": "Kierownik Sprzedaży"},
        "handlowiec1": {"password": "123", "role": "Handlowiec", "name": "Jan Kowalski"},
        "dealer": {"password": "123", "role": "Dealer", "name": "Partner Zewnętrzny"}
    }

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.current_user = None
    st.session_state.role = None

# -----------------------------------------
# LOGOWANIE
# -----------------------------------------
def login_screen():
    st.title("System Wycen Wózków HELI")
    with st.form("login_form"):
        username = st.text_input("Login")
        password = st.text_input("Hasło", type="password")
        submit = st.form_submit_button("Zaloguj")
        if submit:
            users = st.session_state.users_db
            if username in users and users[username]["password"] == password:
                st.session_state.logged_in = True
                st.session_state.current_user = username
                st.session_state.role = users[username]["role"]
                st.rerun()
            else:
                st.error("Błędny login lub hasło!")

# -----------------------------------------
# KALKULATOR (WIDOK)
# -----------------------------------------
def view_calculator():
    st.header("Kalkulator Cen")
    role = st.session_state.role
    
    # Próba wczytania danych z Twojego pliku .xlsm
    df_wozki = load_data()
    
    if df_wozki is None or df_wozki.empty:
        st.error("Nie znaleziono pliku bazy wózków na serwerze! Upewnij się, że wgrałaś plik .xlsm na swój GitHub.")
        return

    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Konfiguracja specyfikacji")
        
        # MAGIA 1: Dynamiczna lista z zakładki Baza_Wozki!
        dostepne_napedy = df_wozki['Typ Napędu'].dropna().unique().tolist()
        typ_napedu = st.selectbox("Typ napędu", dostepne_napedy)
        
        # MAGIA 2: Modele wózków dopasowują się do wybranego napędu!
        dostepne_modele = df_wozki[df_wozki['Typ Napędu'] == typ_napedu]['Model Wózka'].dropna().tolist()
        model = st.selectbox("Model Wózka", dostepne_modele)
        
        maszt = st.selectbox("Maszt", ["Standard 3.0m", "Triplex 4.7m", "Triplex 6.0m"])
        opony = st.selectbox("Opony", ["Pneumatyczne (Standard)", "Pełne (Superelastyczne)"])
        
        marza = st.number_input("Twoja marża (%)", min_value=0, max_value=100, value=10)
        kurs_usd = st.number_input("Kurs USD", value=4.00, step=0.01)

    with col2:
        st.subheader("Podsumowanie dla Klienta")
        
        # POBIERANIE PRAWDZIWEJ CENY Z EXCELA
        wiersz_wozka = df_wozki[df_wozki['Model Wózka'] == model].iloc[0]
        base_price_usd = float(wiersz_wozka['Cena Bazowa (USD)'])
        grupa_tonazowa = wiersz_wozka['Grupa Tonażowa']
        
        # Symulacja cen opcji dodatkowych (do podłączenia pod kolejne zakładki)
        maszt_price_usd = 0
        if maszt == "Triplex 4.7m": maszt_price_usd = 1310
        if maszt == "Triplex 6.0m": maszt_price_usd = 2140
            
        total_usd = base_price_usd + maszt_price_usd
        total_z_marza_usd = total_usd * (1 + (marza/100))
        total_pln = total_z_marza_usd * kurs_usd
        
        # KONTROLA WIDOCZNOŚCI (Role użytkowników)
        if role in ["Administrator", "Menedżer", "Handlowiec"]:
            st.write("---")
            st.write("**Ukryte detale (tylko dla Truck Motor):**")
            st.write(f"Grupa tonażowa: {grupa_tonazowa}")
            st.write(f"Cena wózka fabryka: {base_price_usd:,.2f} USD")
            st.write(f"Cena opcji fabryka: {maszt_price_usd:,.2f} USD")
            st.write("---")
        elif role == "Dealer":
            st.write("*(Szczegóły składowe są ukryte)*")
            
        st.markdown(f'<div class="price-box">Cena dla klienta:<br>{total_pln:,.2f} PLN<br><span style="font-size:14px">({total_z_marza_usd:,.2f} USD)</span></div>', unsafe_allow_html=True)

# -----------------------------------------
# NAWIGACJA
# -----------------------------------------
def main_app():
    with st.sidebar:
        st.write(f"Zalogowany: **{st.session_state.users_db[st.session_state.current_user]['name']}**")
        st.write(f"Rola: {st.session_state.role}")
        st.markdown("---")
        
        menu_options = ["Kalkulator Cen"]
        if st.session_state.role in ["Administrator", "Menedżer"]:
            menu_options.extend(["Zarządzanie Użytkownikami"])
            
        menu_options.append("Wyloguj")
        choice = st.radio("Menu", menu_options)
        
    if choice == "Kalkulator Cen":
        view_calculator()
    elif choice == "Zarządzanie Użytkownikami":
        st.header("Zarządzanie Użytkownikami")
        st.write("Tutaj docelowo będziesz dodawać dealerów i handlowców.")
    elif choice == "Wyloguj":
        st.session_state.logged_in = False
        st.rerun()

if not st.session_state.logged_in:
    login_screen()
else:
    main_app()
