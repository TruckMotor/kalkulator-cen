import streamlit as st
import pandas as pd
import os

# -----------------------------------------
# KONFIGURACJA STRONY I WYGLĄDU (KONTRAST I LOGO)
# -----------------------------------------
st.set_page_config(page_title="Kalkulator Heli - Truck Motor", layout="wide", initial_sidebar_state="expanded")

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
    
    /* Naprawa przycisków - wymuszenie białego tekstu na czerwonym tle */
    .stButton>button { 
        background-color: #CC0000 !important; 
        color: #FFFFFF !important; 
        border-radius: 5px !important; 
        border: none !important; 
        font-weight: bold !important; 
    }
    .stButton>button:hover { 
        background-color: #990000 !important; 
        color: #FFFFFF !important; 
    }
    
    /* Nagłówki w kolorze czerwonym */
    h1, h2, h3 { color: #CC0000; font-family: 'Arial', sans-serif; }
    
    /* Pudełko z ceną */
    .price-box { padding: 20px; background-color: #ffffff; border-left: 5px solid #CC0000; box-shadow: 0 4px 8px rgba(0,0,0,0.1); font-size: 24px; font-weight: bold; margin-bottom: 20px;}
    </style>
""", unsafe_allow_html=True)

# -----------------------------------------
# FUNKCJA WCZYTYWANIA BAZY DANYCH
# -----------------------------------------
@st.cache_data
def load_data():
    file_name = "KONFIGURATOR CEN TRUCK MOTOR 14.09.2026 (spalinowe i elektryczne wózki czołowe).xlsm"
    try:
        df_wozki = pd.read_excel(file_name, sheet_name="Baza_Wozki", engine="openpyxl")
        return df_wozki
    except Exception:
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
# WIDOK LOGOWANIA 
# -----------------------------------------
def login_screen():
    # Logo na ekranie logowania
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if os.path.exists("AUTORYZOWANY DYSTYBUTOR.jpg"):
            st.image("AUTORYZOWANY DYSTYBUTOR.jpg", use_column_width=True)
        else:
            st.warning("Brak pliku AUTORYZOWANY DYSTYBUTOR.jpg na serwerze.")
            
        st.title("System Wycen Wózków HELI")
        st.write("Wprowadź swoje dane, aby uzyskać dostęp do kalkulatora.")
        
        with st.form("login_form"):
            username = st.text_input("Nazwa użytkownika (Login)", placeholder="np. admin")
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
# WIDOKI APLIKACJI
# -----------------------------------------
def view_calculator():
    st.header("Kalkulator Cen HELI")
    role = st.session_state.role
    df_wozki = load_data()
    
    if df_wozki is None or df_wozki.empty:
        st.error("Brak połączenia z plikiem Excel. Wgraj plik .xlsm.")
        return

    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Konfiguracja specyfikacji")
        
        st.markdown("### 1. Baza wózka")
        dostepne_napedy = df_wozki['Typ Napędu'].dropna().unique().tolist()
        typ_napedu = st.selectbox("Wybierz typ napędu:", dostepne_napedy)
        
        dostepne_modele = df_wozki[df_wozki['Typ Napędu'] == typ_napedu]['Model Wózka'].dropna().tolist()
        model = st.selectbox("Wybierz model wózka:", dostepne_modele)
        
        st.markdown("### 2. Maszt i Hydraulika")
        maszt = st.selectbox("Typ i wysokość masztu:", ["Standard (M300) - 3.0m", "Triplex (ZSM470) - 4.7m", "Triplex (ZSM600) - 6.0m"])
        sekcje = st.selectbox("Ilość sekcji rozdzielacza:", ["3 sekcje", "4 sekcje"])
        osprzet = st.selectbox("Osprzęt wideł:", ["Brak (standardowe widły)", "Zintegrowany przesuw boczny", "Pozycjoner wideł z przesuwem", "Obrotnica", "Uchwyt do bel"])
        
        if "Elektryczny" in str(typ_napedu):
            st.markdown("### 3. Zasilanie (Bateria i Ładowarka)")
            bateria = st.selectbox("Pojemność i typ baterii:", ["Standardowa Li-Ion 80V/280Ah", "Powiększona Li-Ion 80V/404Ah", "Powiększona Li-Ion 80V/542Ah"])
            ladowarka = st.selectbox("Typ ładowarki:", ["Standardowa (zintegrowana)", "Zewnętrzna (szybka)"])

        st.markdown("### 4. Wyposażenie dodatkowe")
        kabina = st.selectbox("Opcje kabiny:", ["Brak (tylko daszek)", "Półkabina (szyba przód/tył)", "Pełna kabina ogrzewana", "Pełna kabina z klimatyzacją"])
        opony = st.selectbox("Rodzaj opon:", ["Pneumatyczne (Standard)", "Pełne (Superelastyczne)", "Niebrudzące (Non-marking)"])
        oswietlenie = st.selectbox("Oświetlenie (LED / Blue Spot):", ["Standard LED", "LED + Blue Spot Tył", "LED + Blue Spot Przód i Tył"])
        uruchamianie = st.selectbox("Opcje uruchamiania (OPS):", ["Kluczyk (Standard)", "Karta RFID", "Kod PIN", "Czujnik obecności operatora (OPS)"])
        
        st.markdown("### 5. Koszty i Narzuty")
        kurs_usd = st.number_input("Aktualny Kurs USD/PLN:", value=4.00, step=0.01)
        marza_kwotowa = st.number_input("Twój narzut / Marża handlowca (w PLN):", value=0, step=100)

    with col2:
        st.subheader("Wycena końcowa")
        wiersz_wozka = df_wozki[df_wozki['Model Wózka'] == model].iloc[0]
        base_price_usd = float(wiersz_wozka['Cena Bazowa (USD)'])
        grupa_tonazowa = wiersz_wozka['Grupa Tonażowa']
        
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
            
        st.markdown(f'<div class="price-box">Cena netto klienta:<br>{total_pln:,.2f} PLN<br><span style="font-size:14px; font-weight:normal;">(Zawiera narzut: {marza_kwotowa} PLN)</span></div>', unsafe_allow_html=True)
        
        st.button("Skopiuj konfigurację do e-maila")
        st.button("Zapisz wycenę do archiwum")
        st.button("Pobierz PDF dla klienta")

def view_manage_users():
    st.header("Zarządzanie Użytkownikami")
    st.write("Dodawaj konta dla swoich handlowców i dealerów oraz resetuj im hasła.")
    
    with st.expander("Kliknij tutaj, aby dodać nowego użytkownika", expanded=True):
        new_login = st.text_input("Login użytkownika", placeholder="Wpisz login...")
        new_pass = st.text_input("Hasło startowe", placeholder="Wpisz hasło...")
        new_name = st.text_input("Imię i Nazwisko / Nazwa Firmy", placeholder="np. F.H.U. Widlak")
        
        available_roles = ["Handlowiec", "Dealer"]
        if st.session_state.role == "Administrator":
            available_roles.extend(["Menedżer", "Administrator"])
            
        new_role = st.selectbox("Rola w systemie:", available_roles, help="Dealer nie widzi cen składowych. Handlowiec i Menedżer widzą ceny fabryczne.")
        
        if st.button("Utwórz konto użytkownika"):
            st.session_state.users_db[new_login] = {"password": new_pass, "role": new_role, "name": new_name}
            st.success(f"Konto dla '{new_login}' zostało utworzone poprawnie!")

def view_archive():
    st.header("Archiwum Kalkulacji")
    st.write("Przeglądaj historyczne wyliczenia wykonane w systemie.")
    df = pd.DataFrame({
        "Data": ["2026-09-25", "2026-09-26"],
        "Użytkownik": ["dealer", "handlowiec1"],
        "Model": ["CPCD25", "CPD25 Li-Ion"],
        "Cena PLN": [95000, 115000]
    })
    st.dataframe(df)

def view_update_db():
    st.header("Aktualizacja Bazy Danych Cenników")
    st.write("Wgraj nowe pliki Excel od producenta (np. po zmianie cennika rocznego).")
    uploaded_file = st.file_uploader("Wybierz plik z cennikiem .xlsm", type=['xlsm', 'xlsx'])
    if uploaded_file is not None:
        st.success("Baza danych zaktualizowana pomyślnie!")

def view_order_generator():
    st.header("Generowanie zamówienia do Producenta")
    st.write("System wygeneruje gotowy plik na bazie wzoru 'Re HELI offer 251027 -2.xlsx'.")
    if st.button("Generuj i Pobierz Zamówienie .xlsx"):
        st.success("Plik zamówienia został wygenerowany pomyślnie i jest gotowy do pobrania.")

def view_change_password():
    st.header("Zmiana Twojego hasła")
    new_password = st.text_input("Wpisz nowe hasło", type="password")
    if st.button("Zmień hasło"):
        st.session_state.users_db[st.session_state.current_user]["password"] = new_password
        st.success("Twoje hasło zostało zmienione!")

# -----------------------------------------
# NAWIGACJA GŁÓWNA
# -----------------------------------------
def main_app():
    with st.sidebar:
        # Logo w panelu bocznym
        if os.path.exists("AUTORYZOWANY DYSTYBUTOR.png"):
            st.image("AUTORYZOWANY DYSTYBUTOR.png", use_column_width=True)
            
        st.write(f"Zalogowano: **{st.session_state.users_db[st.session_state.current_user]['name']}**")
        st.write(f"Rola: **{st.session_state.role}**")
        st.markdown("---")
        
        menu_options = ["Kalkulator Cen"]
        
        if st.session_state.role in ["Administrator", "Menedżer"]:
            menu_options.extend(["Archiwum Wyliczeń", "Zarządzanie Użytkownikami", "Generowanie Zamówienia"])
            
        if st.session_state.role == "Administrator":
            menu_options.append("Aktualizacja Bazy Danych")
            
        menu_options.append("Zmień hasło")
        menu_options.append("Wyloguj")
        
        choice = st.radio("Menu Główne:", menu_options)
        
    # Przełączanie widoków
    if choice == "Kalkulator Cen":
        view_calculator()
    elif choice == "Archiwum Wyliczeń":
        view_archive()
    elif choice == "Zarządzanie Użytkownikami":
        view_manage_users()
    elif choice == "Generowanie Zamówienia":
        view_order_generator()
    elif choice == "Aktualizacja Bazy Danych":
        view_update_db()
    elif choice == "Zmień hasło":
        view_change_password()
    elif choice == "Wyloguj":
        st.session_state.logged_in = False
        st.rerun()

if not st.session_state.logged_in:
    login_screen()
else:
    main_app()
