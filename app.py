import streamlit as st
import pandas as pd

# -----------------------------------------
# KONFIGURACJA STRONY I WYGLĄDU (JASNY MOTYW + KONTRAST)
# -----------------------------------------
st.set_page_config(page_title="Kalkulator Heli", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    .stApp { background-color: #f4f4f4; color: #111111; }
    
    /* Pogrubione, czytelne etykiety nad polami */
    label { font-weight: 700 !important; color: #111111 !important; font-size: 14px !important; }
    
    /* Wyraźne białe pola do wpisywania z ciemną ramką */
    .stTextInput input, .stNumberInput input, .stSelectbox div[data-baseweb="select"] { 
        border: 1px solid #777 !important; 
        background-color: #ffffff !important; 
        color: #000000 !important; 
    }
    
    /* Przyciski w kolorach firmy */
    .stButton>button { background-color: #CC0000; color: white; border-radius: 5px; border: none; font-weight: bold; }
    .stButton>button:hover { background-color: #990000; color: white; }
    
    /* Nagłówki */
    h1, h2, h3 { color: #CC0000; font-family: 'Arial', sans-serif; }
    
    /* Pudełko z ceną */
    .price-box { padding: 20px; background-color: #ffffff; border-left: 5px solid #CC0000; box-shadow: 0 4px 8px rgba(0,0,0,0.1); font-size: 24px; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# -----------------------------------------
# FUNKCJA WCZYTYWANIA PRAWDZIWEJ BAZY DANYCH
# -----------------------------------------
@st.cache_data
def load_data():
    file_name = "KONFIGURATOR CEN TRUCK MOTOR 14.09.2026 (spalinowe i elektryczne wózki czołowe).xlsm"
    try:
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
# WIDOK LOGOWANIA (POPRAWIONE OPISY)
# -----------------------------------------
def login_screen():
    st.title("System Wycen Wózków HELI")
    st.write("Wprowadź swoje dane, aby uzyskać dostęp do kalkulatora.")
    
    with st.form("login_form"):
        username = st.text_input("Nazwa użytkownika (Login)", placeholder="np. admin lub handlowiec1")
        password = st.text_input("Hasło dostępu", type="password", placeholder="Wpisz hasło...")
        submit = st.form_submit_button("Zaloguj do systemu")
        
        if submit:
            users = st.session_state.users_db
            if username in users and users[username]["password"] == password:
                st.session_state.logged_in = True
                st.session_state.current_user = username
                st.session_state.role = users[username]["role"]
                st.rerun()
            else:
                st.error("Błędny login lub hasło! Spróbuj ponownie.")

# -----------------------------------------
# KALKULATOR (ROZBUDOWANY O BRAKUJĄCE ZAKŁADKI)
# -----------------------------------------
def view_calculator():
    st.header("Kalkulator Cen")
    role = st.session_state.role
    df_wozki = load_data()
    
    if df_wozki is None or df_wozki.empty:
        st.error("Brak połączenia z plikiem Excel. Wgraj plik .xlsm.")
        return

    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Konfiguracja specyfikacji")
        
        # 1. NAPĘD I MODEL
        st.markdown("### 1. Baza wózka")
        dostepne_napedy = df_wozki['Typ Napędu'].dropna().unique().tolist()
        typ_napedu = st.selectbox("Wybierz typ napędu:", dostepne_napedy)
        
        dostepne_modele = df_wozki[df_wozki['Typ Napędu'] == typ_napedu]['Model Wózka'].dropna().tolist()
        model = st.selectbox("Wybierz model wózka:", dostepne_modele)
        
        # 2. MASZT I HYDRAULIKA
        st.markdown("### 2. Maszt i Hydraulika")
        maszt = st.selectbox("Typ i wysokość masztu:", ["Standard (M300) - 3.0m", "Triplex (ZSM470) - 4.7m", "Triplex (ZSM600) - 6.0m"])
        sekcje = st.selectbox("Ilość sekcji rozdzielacza:", ["3 sekcje", "4 sekcje"])
        osprzet = st.selectbox("Osprzęt wideł:", ["Brak (standardowe widły)", "Zintegrowany przesuw boczny", "Pozycjoner wideł z przesuwem", "Obrotnica", "Uchwyt do bel"])
        
        # 3. ZASILANIE (Pojawia się tylko dla elektryków)
        if "Elektryczny" in str(typ_napedu):
            st.markdown("### 3. Zasilanie (Bateria i Ładowarka)")
            bateria = st.selectbox("Pojemność i typ baterii:", ["Standardowa Li-Ion 80V/280Ah", "Powiększona Li-Ion 80V/404Ah", "Powiększona Li-Ion 80V/542Ah"])
            ladowarka = st.selectbox("Typ ładowarki:", ["Standardowa (zintegrowana)", "Zewnętrzna (szybka)"])

        # 4. WYPOSAŻENIE
        st.markdown("### 4. Wyposażenie dodatkowe")
        kabina = st.selectbox("Opcje kabiny:", ["Brak (tylko daszek)", "Półkabina (szyba przód/tył)", "Pełna kabina ogrzewana", "Pełna kabina z klimatyzacją"])
        opony = st.selectbox("Rodzaj opon:", ["Pneumatyczne (Standard)", "Pełne (Superelastyczne)", "Niebrudzące (Non-marking)"])
        oswietlenie = st.selectbox("Oświetlenie (LED / Blue Spot):", ["Standard LED", "LED + Blue Spot Tył", "LED + Blue Spot Przód i Tył"])
        uruchamianie = st.selectbox("Opcje uruchamiania i bezpieczeństwo (OPS):", ["Kluczyk (Standard)", "Karta RFID", "Kod PIN", "Czujnik obecności operatora (OPS)"])
        
        # 5. USTAWIENIA WALUTOWE
        st.markdown("### 5. Koszty i Narzuty")
        kurs_usd = st.number_input("Aktualny Kurs USD/PLN:", value=4.00, step=0.01)
        marza_kwotowa = st.number_input("Twój narzut / Marża handlowca (w PLN):", value=0, step=100)

    with col2:
        st.subheader("Wycena końcowa")
        wiersz_wozka = df_wozki[df_wozki['Model Wózka'] == model].iloc[0]
        base_price_usd = float(wiersz_wozka['Cena Bazowa (USD)'])
        grupa_tonazowa = wiersz_wozka['Grupa Tonażowa']
        
        # Tymczasowa symulacja ceny opcji - docelowo podepniemy pod tabele
        suma_opcji_usd = 0
        if "Triplex 4.7m" in maszt: suma_opcji_usd += 1160
        if "Pełna kabina" in kabina: suma_opcji_usd += 1500
        
        total_usd = base_price_usd + suma_opcji_usd
        total_pln = (total_usd * kurs_usd) + marza_kwotowa
        
        if role in ["Administrator", "Menedżer", "Handlowiec"]:
            st.write("---")
            st.write("**Detale wewnętrzne (Niewidoczne dla Dealera):**")
            st.write(f"Grupa tonażowa: {grupa_tonazowa}")
            st.write(f"Baza (Fabryka): {base_price_usd:,.2f} USD")
            st.write(f"Opcje (Fabryka): {suma_opcji_usd:,.2f} USD")
            st.write("---")
        elif role == "Dealer":
            st.write("*(Szczegóły składowe są zastrzeżone)*")
            
        st.markdown(f'<div class="price-box">Cena netto klienta:<br>{total_pln:,.2f} PLN<br><span style="font-size:14px; font-weight:normal;">(Zawiera Twój narzut: {marza_kwotowa} PLN)</span></div>', unsafe_allow_html=True)
        
        st.button("Skopiuj konfigurację wózka")
        st.button("Zapisz wycenę do archiwum")

# -----------------------------------------
# WIDOK DODAWANIA UŻYTKOWNIKA (POPRAWIONE OPISY)
# -----------------------------------------
def view_manage_users():
    st.header("Zarządzanie Użytkownikami")
    st.write("Tutaj możesz zakładać konta dla swoich handlowców oraz dealerów, określając ich dostęp do cen.")
    
    with st.expander("Kliknij tutaj, aby dodać nowego użytkownika", expanded=True):
        new_login = st.text_input("Login (np. nazwa dealera lub imię)", placeholder="Wpisz login...")
        new_pass = st.text_input("Hasło startowe", placeholder="Wpisz hasło...")
        new_name = st.text_input("Imię i Nazwisko / Nazwa Firmy", placeholder="np. F.H.U. Widlak-Pol")
        
        available_roles = ["Handlowiec", "Dealer"]
        if st.session_state.role == "Administrator":
            available_roles.extend(["Menedżer", "Administrator"])
            
        new_role = st.selectbox("Wybierz uprawnienia (Rola w systemie):", available_roles, help="Dealer nie widzi cen składowych. Handlowiec i Menedżer widzą ceny fabryczne.")
        
        if st.button("Utwórz konto użytkownika"):
            st.session_state.users_db[new_login] = {"password": new_pass, "role": new_role, "name": new_name}
            st.success(f"Konto dla '{new_login}' zostało utworzone poprawnie!")

# -----------------------------------------
# NAWIGACJA
# -----------------------------------------
def main_app():
    with st.sidebar:
        st.write(f"Zalogowano jako: **{st.session_state.users_db[st.session_state.current_user]['name']}**")
        st.write(f"Uprawnienia: **{st.session_state.role}**")
        st.markdown("---")
        
        menu_options = ["Kalkulator Cen"]
        if st.session_state.role in ["Administrator", "Menedżer"]:
            menu_options.append("Zarządzanie Użytkownikami")
            
        menu_options.append("Wyloguj")
        choice = st.radio("Menu Główne:", menu_options)
        
    if choice == "Kalkulator Cen":
        view_calculator()
    elif choice == "Zarządzanie Użytkownikami":
        view_manage_users()
    elif choice == "Wyloguj":
        st.session_state.logged_in = False
        st.rerun()

if not st.session_state.logged_in:
    login_screen()
else:
    main_app()
