import streamlit as st
import pandas as pd
import os

# -----------------------------------------
# KONFIGURACJA STRONY I WYGLĄDU 
# -----------------------------------------
st.set_page_config(page_title="Kalkulator Heli - Truck Motor", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    .stApp { background-color: #f4f4f4; color: #111111; }
    label { font-weight: 700 !important; color: #111111 !important; font-size: 14px !important; margin-bottom: -5px; }
    .stTextInput input, .stNumberInput input, .stSelectbox div[data-baseweb="select"] { 
        border: 1px solid #777 !important; 
        background-color: #ffffff !important; 
        color: #000000 !important; 
    }
    .stButton>button { 
        background-color: #CC0000 !important; 
        color: #FFFFFF !important; 
        border-radius: 5px !important; 
        border: none !important; 
        font-weight: bold !important; 
    }
    .stButton>button:hover { background-color: #990000 !important; color: #FFFFFF !important; }
    h1, h2, h3 { color: #CC0000; font-family: 'Arial', sans-serif; margin-bottom: 5px; margin-top: 15px;}
    .price-box { padding: 20px; background-color: #ffffff; border-left: 5px solid #CC0000; box-shadow: 0 4px 8px rgba(0,0,0,0.1); font-size: 24px; font-weight: bold; margin-bottom: 20px;}
    </style>
""", unsafe_allow_html=True)

# -----------------------------------------
# FUNKCJE WCZYTYWANIA ZŁOŻONEJ BAZY DANYCH
# -----------------------------------------
@st.cache_data
def load_all_data():
    file_name = "KONFIGURATOR CEN TRUCK MOTOR 14.09.2026 (spalinowe i elektryczne wózki czołowe).xlsm"
    data = {}
    try:
        # Wczytujemy wózki
        data['wozki'] = pd.read_excel(file_name, sheet_name="Baza_Wozki", engine="openpyxl")
        
        # Wczytujemy surowe tabele
        data['maszty_raw'] = pd.read_excel(file_name, sheet_name="Baza_Maszty", header=None, engine="openpyxl")
        data['opony_raw'] = pd.read_excel(file_name, sheet_name="Baza_Opony", header=None, engine="openpyxl")
        data['kabiny_raw'] = pd.read_excel(file_name, sheet_name="Baza_Kabina", header=None, engine="openpyxl")
        data['widly_raw'] = pd.read_excel(file_name, sheet_name="Baza_Widły", header=None, engine="openpyxl")
        
        return data
    except Exception as e:
        st.error(f"Błąd odczytu pliku: {e}")
        return None

def get_options_from_raw(df_raw, drive_type, series, tonnage):
    """Filtruje tabele takie jak Baza_Opony, gdzie wiersz 0 to Napęd, wiersz 1 to Seria, wiersz 2 to Tonaż"""
    options = {}
    # Szukamy właściwej kolumny
    target_col = None
    for col in range(1, len(df_raw.columns)):
        try:
            val_drive = str(df_raw.iloc[0, col]).strip()
            val_series = str(df_raw.iloc[1, col]).strip()
            val_tonnage = str(df_raw.iloc[2, col]).strip()
            
            # Weryfikacja
            if (val_drive == str(drive_type) and val_series == str(series) and val_tonnage == str(tonnage)):
                target_col = col
                break
        except:
            continue
            
    if target_col is not None:
        for row in range(3, len(df_raw)):
            option_name = str(df_raw.iloc[row, 0]).strip()
            price = df_raw.iloc[row, target_col]
            if pd.notna(price) and str(price).strip() != 'nan' and option_name != 'nan':
                options[option_name] = float(price)
    return options

def get_mast_options(df_maszty, tonnage, sections="3 sekcje"):
    """Filtruje Baza_Maszty, gdzie wiersz 0 to ilość sekcji, a wiersz 1 to Tonaż"""
    options = {}
    target_col = None
    for col in range(1, len(df_maszty.columns)):
        try:
            val_sections = str(df_maszty.iloc[0, col]).strip()
            val_tonnage = str(df_maszty.iloc[1, col]).strip()
            
            if val_sections == str(sections) and val_tonnage == str(tonnage):
                target_col = col
                break
        except:
            continue
            
    if target_col is not None:
        for row in range(2, len(df_maszty)):
            mast_name = str(df_maszty.iloc[row, 0]).strip()
            price = df_maszty.iloc[row, target_col]
            if pd.notna(price) and str(price).strip() != 'nan' and mast_name != 'nan':
                options[mast_name] = float(price)
    return options

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

# -----------------------------------------
# WIDOK LOGOWANIA 
# -----------------------------------------
def login_screen():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if os.path.exists("AUTORYZOWANY DYSTYBUTOR.png"):
            try: st.image("AUTORYZOWANY DYSTYBUTOR.png", use_container_width=True)
            except: pass
            
        st.title("System Wycen Wózków HELI")
        st.write("Wprowadź swoje dane, aby uzyskać dostęp do kalkulatora.")
        
        with st.form("login_form"):
            username = st.text_input("Nazwa użytkownika (Login)", placeholder="np. admin")
            password = st.text_input("Hasło dostępu", type="password", placeholder="Wpisz hasło...")
            submit = st.form_submit_button("Zaloguj do systemu")
            
            if submit:
                if username in st.session_state.users_db and st.session_state.users_db[username]["password"] == password:
                    st.session_state.logged_in = True
                    st.session_state.current_user = username
                    st.session_state.role = st.session_state.users_db[username]["role"]
                    st.rerun()
                else:
                    st.error("Błędny login lub hasło!")

# -----------------------------------------
# KALKULATOR GŁÓWNY
# -----------------------------------------
def view_calculator():
    st.header("Kalkulator Cen HELI")
    role = st.session_state.role
    db = load_all_data()
    
    if db is None: return

    df_wozki = db['wozki']
    
    col1, col2 = st.columns([7, 3])
    
    with col1:
        st.markdown("### Baza wózka")
        c1, c2 = st.columns(2)
        dostepne_napedy = df_wozki['Typ Napędu'].dropna().unique().tolist()
        typ_napedu = c1.selectbox("Wybierz typ napędu:", dostepne_napedy)
        dostepne_modele = df_wozki[df_wozki['Typ Napędu'] == typ_napedu]['Model Wózka'].dropna().tolist()
        model = c2.selectbox("Wybierz model wózka:", dostepne_modele)
        
        # Pobieranie kluczowych parametrów wybranego wózka
        wiersz_wozka = df_wozki[df_wozki['Model Wózka'] == model].iloc[0]
        base_price_usd = float(wiersz_wozka['Cena Bazowa (USD)'])
        grupa_tonazowa = str(wiersz_wozka['Grupa Tonażowa']).strip()
        seria = str(wiersz_wozka['Seria']).strip()
        
        # Ściąganie dostępnych opcji z bazy
        maszty_dict = get_mast_options(db['maszty_raw'], grupa_tonazowa, "3 sekcje") # docelowo można dodać wybór sekcji
        opony_dict = get_options_from_raw(db['opony_raw'], typ_napedu, seria, grupa_tonazowa)
        kabiny_dict = get_options_from_raw(db['kabiny_raw'], typ_napedu, seria, grupa_tonazowa)
        widly_dict = get_options_from_raw(db['widly_raw'], typ_napedu, seria, grupa_tonazowa)

        st.markdown("### Maszt i Hydraulika")
        c3, c4, c5 = st.columns(3)
        lista_masztow = list(maszty_dict.keys()) if maszty_dict else ["Brak masztów dla tego modelu w bazie"]
        maszt = c3.selectbox("Typ i wysokość masztu:", lista_masztow)
        
        lista_widel = list(widly_dict.keys()) if widly_dict else ["Brak wideł w bazie"]
        widly = c4.selectbox("Wymiar wideł:", lista_widel)
        
        osprzet = c5.selectbox("Osprzęt:", ["Brak", "Zintegrowany przesuw boczny", "Pozycjoner", "Obrotnica"])
        
        st.markdown("### Wyposażenie dodatkowe")
        c6, c7 = st.columns(2)
        
        lista_kabin = list(kabiny_dict.keys()) if kabiny_dict else ["Brak opcji kabiny"]
        kabina = c6.selectbox("Opcje kabiny:", lista_kabin)
        
        lista_opon = list(opony_dict.keys()) if opony_dict else ["Brak opcji opon"]
        opony = c7.selectbox("Rodzaj opon:", lista_opon)
        
        if "Elektryczny" in str(typ_napedu):
            st.markdown("### Zasilanie")
            c10, c11 = st.columns(2)
            bateria = c10.selectbox("Bateria:", ["Standard", "Powiększona"])
            ladowarka = c11.selectbox("Ładowarka:", ["Standard", "Szybka"])

        st.markdown("### Koszty i Narzuty")
        c12, c13 = st.columns(2)
        kurs_usd = c12.number_input("Aktualny Kurs USD/PLN:", value=4.00, step=0.01)
        marza_kwotowa = c13.number_input("Twój narzut (w PLN):", value=0, step=100)

    with col2:
        st.subheader("Wycena końcowa")
        
        # Wyliczanie cen na podstawie bazy
        maszt_price = maszty_dict.get(maszt, 0)
        opony_price = opony_dict.get(opony, 0)
        kabina_price = kabiny_dict.get(kabina, 0)
        widly_price = widly_dict.get(widly, 0)
        
        suma_opcji_usd = maszt_price + opony_price + kabina_price + widly_price
        total_usd = base_price_usd + suma_opcji_usd
        total_pln = (total_usd * kurs_usd) + marza_kwotowa
        
        if role in ["Administrator", "Menedżer", "Handlowiec"]:
            st.write("---")
            st.write("**Detale wewnętrzne (Niewidoczne dla Dealera):**")
            st.write(f"Tonaż: **{grupa_tonazowa}** | Seria: **{seria}**")
            st.write(f"Baza (Fabryka): **{base_price_usd:,.2f} USD**")
            st.write(f"Opcje (Fabryka): **{suma_opcji_usd:,.2f} USD**")
            st.write("---")
        elif role == "Dealer":
            st.write("*(Szczegóły składowe są zastrzeżone)*")
            
        st.markdown(f'<div class="price-box">Cena netto klienta:<br>{total_pln:,.2f} PLN<br><span style="font-size:14px; font-weight:normal;">(Zawiera narzut: {marza_kwotowa} PLN)</span></div>', unsafe_allow_html=True)
        
        st.button("Skopiuj konfigurację", use_container_width=True)
        st.button("Zapisz wycenę", use_container_width=True)
        st.button("Pobierz PDF", use_container_width=True)

# -----------------------------------------
# INNE WIDOKI (ADMIN)
# -----------------------------------------
def view_manage_users():
    st.header("Zarządzanie Użytkownikami")
    st.write("Dodawaj konta dla swoich handlowców i dealerów oraz resetuj im hasła.")
    with st.expander("Kliknij tutaj, aby dodać użytkownika", expanded=True):
        new_login = st.text_input("Login użytkownika")
        new_pass = st.text_input("Hasło startowe")
        new_name = st.text_input("Imię i Nazwisko / Nazwa Firmy")
        available_roles = ["Handlowiec", "Dealer"]
        if st.session_state.role == "Administrator": available_roles.extend(["Menedżer", "Administrator"])
        new_role = st.selectbox("Rola w systemie:", available_roles)
        if st.button("Utwórz konto użytkownika"):
            st.session_state.users_db[new_login] = {"password": new_pass, "role": new_role, "name": new_name}
            st.success(f"Konto utworzone!")

def view_archive():
    st.header("Archiwum Kalkulacji")
    st.write("Historia wyliczeń.")

def view_update_db():
    st.header("Aktualizacja Bazy Danych Cenników")
    uploaded_file = st.file_uploader("Wybierz plik z cennikiem .xlsm", type=['xlsm', 'xlsx'])
    if uploaded_file is not None: st.success("Zaktualizowano!")

def view_order_generator():
    st.header("Generowanie zamówienia do Producenta")
    if st.button("Generuj Zamówienie .xlsx"): st.success("Gotowe do pobrania.")

def view_change_password():
    st.header("Zmiana Twojego hasła")
    new_password = st.text_input("Wpisz nowe hasło", type="password")
    if st.button("Zmień hasło"):
        st.session_state.users_db[st.session_state.current_user]["password"] = new_password
        st.success("Zmieniono!")

# -----------------------------------------
# NAWIGACJA GŁÓWNA
# -----------------------------------------
def main_app():
    with st.sidebar:
        if os.path.exists("AUTORYZOWANY DYSTYBUTOR.png"):
            try: st.image("AUTORYZOWANY DYSTYBUTOR.png", use_container_width=True)
            except: pass
            
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
        
    if choice == "Kalkulator Cen": view_calculator()
    elif choice == "Archiwum Wyliczeń": view_archive()
    elif choice == "Zarządzanie Użytkownikami": view_manage_users()
    elif choice == "Generowanie Zamówienia": view_order_generator()
    elif choice == "Aktualizacja Bazy Danych": view_update_db()
    elif choice == "Zmień hasło": view_change_password()
    elif choice == "Wyloguj":
        st.session_state.logged_in = False
        st.rerun()

if not st.session_state.logged_in:
    login_screen()
else:
    main_app()
