import streamlit as st
import pandas as pd
import datetime

# -----------------------------------------
# KONFIGURACJA STRONY I WYGLĄDU (Czarny, Czerwony, Biały)
# -----------------------------------------
st.set_page_config(page_title="Kalkulator Heli", layout="wide", initial_sidebar_state="expanded")

# Wstrzykiwanie niestandardowego kodu CSS dla kolorystyki korporacyjnej
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; color: #000000; }
    .css-1d391kg { background-color: #111111; } /* Sidebar background */
    .stButton>button { background-color: #CC0000; color: white; border-radius: 5px; border: none; font-weight: bold; }
    .stButton>button:hover { background-color: #990000; color: white; }
    h1, h2, h3 { color: #CC0000; font-family: 'Arial', sans-serif; }
    .price-box { padding: 20px; background-color: #f8f9fa; border-left: 5px solid #CC0000; font-size: 24px; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# -----------------------------------------
# BAZA UŻYTKOWNIKÓW I ROL (Symulacja bazy danych)
# -----------------------------------------
if 'users_db' not in st.session_state:
    st.session_state.users_db = {
        "admin": {"password": "123", "role": "Administrator", "name": "Szefowa"},
        "kierownik": {"password": "123", "role": "Menedżer", "name": "Kierownik Sprzedaży"},
        "handlowiec1": {"password": "123", "role": "Handlowiec", "name": "Jan Kowalski"},
        "dealer_wawa": {"password": "123", "role": "Dealer", "name": "Partner Warszawa"}
    }

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.current_user = None
    st.session_state.role = None

# -----------------------------------------
# SYSTEM LOGOWANIA
# -----------------------------------------
def login_screen():
    # Wyświetlanie logo firmy na ekranie logowania
    try:
        st.image("AUTORYZOWANY DYSTYBUTOR.jpg", width=300)
    except:
        st.write("*(Tu pojawi się logo AUTORYZOWANY DYSTYBUTOR.jpg)*")
        
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
# FUNKCJE APLIKACJI (WIDOKI)
# -----------------------------------------
def view_calculator():
    st.header("Kalkulator Cen")
    role = st.session_state.role
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Konfiguracja specyfikacji")
        # Pola wyboru podobne do Excela
        typ_napedu = st.selectbox("Typ napędu", ["Spalinowy", "Elektryczny Li-Ion"])
        model = st.selectbox("Model Wózka", ["CPCD25-KU24HG3", "CPD25-GB2LI-M"])
        maszt = st.selectbox("Maszt", ["Standard 3.0m", "Triplex 4.7m", "Triplex 6.0m"])
        opony = st.selectbox("Opony", ["Pneumatyczne", "Superelastyczne"])
        
        marza = st.number_input("Twoja marża (%)", min_value=0, max_value=100, value=10)
        kurs_usd = st.number_input("Kurs USD", value=4.00, step=0.01)

    with col2:
        st.subheader("Podsumowanie dla Klienta")
        
        # Symulacja obliczeń (w pełnej wersji zaciąga dane z bazy w Pandas)
        base_price_usd = 19100
        maszt_price_usd = 1310
        total_usd = base_price_usd + maszt_price_usd
        total_z_marza_usd = total_usd * (1 + (marza/100))
        total_pln = total_z_marza_usd * kurs_usd
        
        # WIDOK ZALEŻNY OD ROLI
        if role in ["Administrator", "Menedżer", "Handlowiec"]:
            st.write("---")
            st.write("**Ukryte detale (tylko dla pracowników):**")
            st.write(f"Cena bazowa: {base_price_usd} USD")
            st.write(f"Dopłata maszt: {maszt_price_usd} USD")
            st.write(f"Suma netto fabryka: {total_usd} USD")
            st.write("---")
            
        elif role == "Dealer":
            st.write("*(Szczegóły składowe są ukryte)*")
            
        st.markdown(f'<div class="price-box">Cena dla klienta:<br>{total_pln:,.2f} PLN<br><span style="font-size:14px">({total_z_marza_usd:,.2f} USD)</span></div>', unsafe_allow_html=True)
        
        if st.button("Zapisz wycenę do archiwum"):
            st.success("Wycena zapisana pomyślnie!")
            
        if st.button("Pobierz specyfikację (PDF)"):
            st.info("Generowanie PDF ze specyfikacją do wydruku...")

def view_manage_users():
    st.header("Zarządzanie Użytkownikami")
    st.write("Dodawanie kont i zmiana haseł.")
    
    with st.expander("Dodaj nowego użytkownika"):
        new_login = st.text_input("Nowy login")
        new_pass = st.text_input("Hasło")
        new_name = st.text_input("Imię i Nazwisko / Nazwa Firmy")
        # Menedżer nie może stworzyć Administratora
        available_roles = ["Handlowiec", "Dealer"]
        if st.session_state.role == "Administrator":
            available_roles.append("Menedżer")
            available_roles.append("Administrator")
            
        new_role = st.selectbox("Rola", available_roles)
        
        if st.button("Utwórz konto"):
            st.session_state.users_db[new_login] = {"password": new_pass, "role": new_role, "name": new_name}
            st.success(f"Dodano użytkownika: {new_login}")

def view_update_db():
    st.header("Aktualizacja Bazy Danych Cenników")
    st.write("Wgraj nowe pliki Excel od producenta.")
    uploaded_file = st.file_uploader("Wybierz plik z cennikiem", type=['xlsx'])
    if uploaded_file is not None:
        st.success("Baza danych zaktualizowana pomyślnie!")

def view_archive():
    st.header("Archiwum Kalkulacji")
    st.write("Przeglądaj historyczne wyliczenia wykonane przez sieć sprzedaży.")
    # Symulacja tabeli
    df = pd.DataFrame({
        "Data": ["2026-09-25", "2026-09-26"],
        "Użytkownik": ["dealer_wawa", "handlowiec1"],
        "Wózek": ["CPCD25", "CPD25 Li-Ion"],
        "Kwota PLN": [95000, 115000]
    })
    st.dataframe(df)

def view_order_generator():
    st.header("Generowanie zamówienia (Excel)")
    st.write("Wygeneruj gotowy plik zamówienia do fabryki na bazie pliku: 'Re HELI offer 251027 -2.xlsx'")
    if st.button("Generuj i Pobierz Zamówienie .xlsx"):
        st.success("Plik zamówienia został wygenerowany!")

# -----------------------------------------
# GŁÓWNA STRUKTURA I NAWIGACJA (PANEL BOCZNY)
# -----------------------------------------
def main_app():
    # Sidebar
    with st.sidebar:
        try:
            st.image("AUTORYZOWANY DYSTYBUTOR.jpg", use_column_width=True)
        except:
            st.write("[LOGO HELI]")
            
        st.write(f"Zalogowany: **{st.session_state.users_db[st.session_state.current_user]['name']}**")
        st.write(f"Rola: {st.session_state.role}")
        st.markdown("---")
        
        menu_options = ["Kalkulator Cen"]
        
        if st.session_state.role in ["Administrator", "Menedżer"]:
            menu_options.extend(["Archiwum Wyliczeń", "Zarządzanie Użytkownikami", "Generuj Zamówienie HELI"])
            
        if st.session_state.role == "Administrator":
            menu_options.append("Aktualizacja Bazy Danych")
            
        menu_options.append("Zmień swoje hasło")
        menu_options.append("Wyloguj")
        
        choice = st.radio("Menu", menu_options)
        
    # Routing
    if choice == "Kalkulator Cen":
        view_calculator()
    elif choice == "Archiwum Wyliczeń":
        view_archive()
    elif choice == "Zarządzanie Użytkownikami":
        view_manage_users()
    elif choice == "Generuj Zamówienie HELI":
        view_order_generator()
    elif choice == "Aktualizacja Bazy Danych":
        view_update_db()
    elif choice == "Zmień swoje hasło":
        st.header("Zmiana hasła")
        st.text_input("Nowe hasło", type="password")
        if st.button("Zapisz hasło"):
            st.success("Hasło zmienione!")
    elif choice == "Wyloguj":
        st.session_state.logged_in = False
        st.rerun()

# -----------------------------------------
# URUCHOMIENIE
# -----------------------------------------
if not st.session_state.logged_in:
    login_screen()
else:
    main_app()