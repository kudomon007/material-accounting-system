import streamlit as st
import sqlite3
from datetime import date, timedelta
import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from datetime import date, timedelta, datetime 
import os
import io
import bcrypt

def hash_password(password):
    """Hash a password using bcrypt"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def verify_password(plain_password, hashed_password):
    """Verify a plain password against a stored hash"""
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
    
def migrate_passwords():
    """One-time migration to hash existing plain text passwords"""
    db.execute("SELECT id, password FROM users")
    users = db.fetchall()
    
    for user_id, plain_password in users:
 
        if not plain_password.startswith('$2b$'):
            hashed = hash_password(plain_password)
            db.execute("UPDATE users SET password = ? WHERE id = ?", (hashed, user_id))
    
    conn.commit()
    print(f"Migrated {len(users)} users to hashed passwords")

# Set page config FIRST
st.set_page_config(
    page_title="Projekta Sistēma",
    page_icon="🏗",
    layout="wide"
)

 Session State Initialization 
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user = None
if "current_page" not in st.session_state:
    st.session_state.current_page = "Dashboard"
if "active_work_date" not in st.session_state:
    st.session_state.active_work_date = date.today()

# Import styles 
try:
    from styles import MAIN_STYLES, COLORS
    from components import sidebar_header, navigation_menu
    HAS_CUSTOM_STYLES = True
except ImportError as e:
    print(f"Warning: Could not import custom styles: {e}")
    HAS_CUSTOM_STYLES = False
    MAIN_STYLES = ""
    COLORS = {}
    
    #  fallback functions
    def sidebar_header(user):
        """Fallback sidebar header"""
        st.markdown(f"""
        <div style="padding: 10px; color: white;">
            <h3>Projekta Sistēma</h3>
            <p>Lietotājs: {user[1]}</p>
            <p>Loma: {user[3]}</p>
        </div>
        <hr>
        """, unsafe_allow_html=True)
    
    def navigation_menu(role):
        """Fallback navigation menu"""
        if role == "admin":
            return {"Dashboard": "📊", "Lietotāji": "👥", "Projekti": "🏗️", "Piesaistes": "🔗"}
        elif role == "manager":
            return {"Dashboard": "📊", "Rēķini": "📄"}
        else:
            return {"Dashboard": "📊", "Materiāli": "📦", "Stundas": "⏱️", "Transports": "🚗"}

# Apply MAIN_STYLES 
if HAS_CUSTOM_STYLES and MAIN_STYLES:
    st.markdown(MAIN_STYLES, unsafe_allow_html=True)

# Constants
DAY_RATE = 10.0
NIGHT_RATE = 15.0

#  Database Connection 
try:
    # Create database directory 
    os.makedirs("database", exist_ok=True)
    conn = sqlite3.connect("database/materials.db", check_same_thread=False)
    db = conn.cursor()
except sqlite3.Error as e:
    st.error(f"Database connection error: {e}")
    st.stop()

# PDF Generation 
def generate_invoice_pdf(invoice_id, user_id, project_id, start_date, end_date, filename="rekins.pdf"):
    """
    Ģenerē PDF rēķinu un atgriež faila nosaukumu
    """
    try:
        print("\n=== SĀK PDF ĢENERĀCIJU ===")
        print(f"Parametri: invoice_id={invoice_id}, user_id={user_id}, project_id={project_id}")
        print(f"Periods: {start_date} - {end_date}")
        print(f"Faila nosaukums: {filename}")
        
    
        current_dir = os.getcwd()
        print(f"Pašreizējā direktorija: {current_dir}")
        

        c = canvas.Canvas(filename, pagesize=A4)
        
      
        font_loaded = False
        try:
       
            if os.path.exists('DejaVuSans.ttf'):
                pdfmetrics.registerFont(TTFont('DejaVuSans', 'DejaVuSans.ttf'))
                c.setFont("DejaVuSans", 11)
                print("✓ DejaVuSans fonts ielādēts (atbalsta garumzīmes)")
                font_loaded = True
            else:
  
                c.setFont("Helvetica", 11)
                print("⚠ DejaVuSans.ttf nav atrasts, izmantoju Helvetica (bez garumzīmēm)")
        except Exception as font_error:
            print(f"Fonta kļūda: {font_error}")
            c.setFont("Helvetica", 11)
        
        # PDF 
        y = 800
        c.drawString(50, y, "RĒĶINS")
        y -= 20
        c.drawString(50, y, f"Rēķins Nr. {invoice_id}")
        y -= 20
        c.drawString(50, y, f"Periods: {start_date} – {end_date}")
        y -= 20
        c.line(50, y, 550, y)
        y -= 30
        
        # Materials
        c.drawString(50, y, "Materiāli:")
        y -= 20
        
        db.execute("""
            SELECT m.name, SUM(um.quantity), m.price
            FROM usage_materials um
            JOIN materials m ON um.material_id = m.id
            WHERE um.user_id=? AND um.project_id=? AND um.date BETWEEN ? AND ?
            GROUP BY m.id
        """, (user_id, project_id, start_date, end_date))
        
        materials = db.fetchall()
        print(f"Atrasti {len(materials)} materiāli")
        
        mat_total = 0
        if materials:
            for name, qty, price in materials:
                cost = qty * price
                mat_total += cost
                c.drawString(60, y, f"{name}: {qty} x {price}€ = {cost:.2f}€")
                y -= 15
        else:
            c.drawString(60, y, "Nav materiālu")
            y -= 15
        
        # work hours
        y -= 10
        c.drawString(50, y, "Darba stundas:")
        y -= 20
        
        db.execute("""
            SELECT SUM(hours_day), SUM(hours_night)
            FROM work_hours
            WHERE user_id=? AND project_id=? AND date BETWEEN ? AND ?
        """, (user_id, project_id, start_date, end_date))
        
        day_hours, night_hours = db.fetchone()
        day_hours = day_hours or 0
        night_hours = night_hours or 0
        hours_cost = day_hours * DAY_RATE + night_hours * NIGHT_RATE
        print(f"Stundas: {day_hours}d + {night_hours}n = {hours_cost}€")
        
        if day_hours > 0 or night_hours > 0:
            c.drawString(60, y, f"Dienas stundas: {day_hours}h, Nakts stundas: {night_hours}h = {hours_cost:.2f}€")
        else:
            c.drawString(60, y, "Nav stundu")
        y -= 15
        
        # Transport
        y -= 10
        c.drawString(50, y, "Transports:")
        y -= 20
        
        db.execute("""
            SELECT SUM(liters), AVG(price_per_liter)
            FROM transport_usage
            WHERE user_id=? AND project_id=? AND date BETWEEN ? AND ?
        """, (user_id, project_id, start_date, end_date))
        
        liters, avg_price = db.fetchone()
        liters = liters or 0
        avg_price = avg_price or 0
        transport_cost = liters * avg_price
        print(f"Transports: {liters}L x {avg_price}€ = {transport_cost}€")
        
        if liters > 0:
            c.drawString(60, y, f"{liters} L × {avg_price:.2f}€ = {transport_cost:.2f}€")
        else:
            c.drawString(60, y, "Nav transporta")
        y -= 15
        
        #together
        total = mat_total + hours_cost + transport_cost
        y -= 20
        c.line(50, y, 550, y)
        y -= 20
        c.drawString(50, y, f"KOPĀ: {total:.2f} €")
        
        # Save PDF
        c.save()
        print(f"✓ PDF saglabāts: {filename}")
        
        
        if os.path.exists(filename):
            file_size = os.path.getsize(filename)
            print(f"✓ Fails eksistē, izmērs: {file_size} baiti")
            return filename
        else:
            print(f"✗ Fails NAV izveidots: {filename}")
            return None
            
    except Exception as e:
        print(f"✗ KĻŪDA PDF ĢENERĀCIJĀ: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

# Database Initialization 
def init_db():
    # Users
    db.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        role TEXT
    )
    """)

    # Projects
    db.execute("""
    CREATE TABLE IF NOT EXISTS projects (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        client_name TEXT,
        address TEXT
    )
    """)

    # Materials
    db.execute("""
    CREATE TABLE IF NOT EXISTS materials (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        unit TEXT,
        price REAL
    )
    """)

    # Material usage
    db.execute("""
    CREATE TABLE IF NOT EXISTS usage_materials (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        material_id INTEGER,
        quantity REAL,
        project_id INTEGER,
        source TEXT,
        date TEXT,
        FOREIGN KEY(user_id) REFERENCES users(id),
        FOREIGN KEY(material_id) REFERENCES materials(id),
        FOREIGN KEY(project_id) REFERENCES projects(id)
    )
    """)

    # Work hours
    db.execute("""
    CREATE TABLE IF NOT EXISTS work_hours (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        project_id INTEGER,
        date TEXT,
        hours_day REAL,
        hours_night REAL,
        FOREIGN KEY(user_id) REFERENCES users(id),
        FOREIGN KEY(project_id) REFERENCES projects(id)
    )
    """)

    # Transport usage
    db.execute("""
    CREATE TABLE IF NOT EXISTS transport_usage (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        project_id INTEGER,
        liters REAL,
        price_per_liter REAL,
        date TEXT,
        FOREIGN KEY(user_id) REFERENCES users(id),
        FOREIGN KEY(project_id) REFERENCES projects(id)
    )
    """)
    
    # Invoices
    db.execute("""
    CREATE TABLE IF NOT EXISTS invoices (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        project_id INTEGER,
        created_at TEXT
    )
    """)
    
    # User projects association
    db.execute("""
    CREATE TABLE IF NOT EXISTS user_projects (
        user_id INTEGER,
        project_id INTEGER,
        PRIMARY KEY (user_id, project_id),
        FOREIGN KEY(user_id) REFERENCES users(id),
        FOREIGN KEY(project_id) REFERENCES projects(id)
    )
    """)
    conn.commit()
    
    admin_hash = hash_password("admin")
    manager_hash = hash_password("manager")
    worker_hash = hash_password("worker")
    
    # Insert users with HASHED passwords
    db.execute("INSERT OR IGNORE INTO users (username, password, role) VALUES (?,?,?)", 
               ("admin", admin_hash, "admin"))
    db.execute("INSERT OR IGNORE INTO users (username, password, role) VALUES (?,?,?)", 
               ("manager", manager_hash, "manager"))
    db.execute("INSERT OR IGNORE INTO users (username, password, role) VALUES (?,?,?)", 
               ("worker", worker_hash, "worker"))

    # Sample materials
    db.execute("SELECT COUNT(*) FROM materials")
    if db.fetchone()[0] == 0:
        materials = [
            ("Cements", "kg", 5.0),
            ("Smiltis", "kg", 0.5),
            ("Ūdens", "L", 0.2),
            ("Koka dēļi", "gab", 2.0)
        ]
        db.executemany("INSERT INTO materials (name, unit, price) VALUES (?,?,?)", materials)

    # Sample project
    db.execute("SELECT COUNT(*) FROM projects")
    if db.fetchone()[0] == 0:
        db.execute(
            "INSERT INTO projects (name, client_name, address) VALUES (?,?,?)",
            ("Demo Projekts", "Klients SIA", "Rīgas iela 1")
        )
    conn.commit()

# Initialize database
init_db()

#  DASHBOARD FUNCTIONS\
def worker_dashboard(user):
    st.markdown('<h1 class="gradient-header">📊 Worker Dashboard</h1>', unsafe_allow_html=True)

    db.execute("""
        SELECT p.id, p.name
        FROM projects p
        JOIN user_projects up ON p.id = up.project_id
        WHERE up.user_id = ?
    """, (user[0],))
    projects = db.fetchall()

    total_hours_week = 0
    total_hours_month = 0
    active_project = projects[0][1] if projects else "Nav"

    for p_id, _ in projects:
        db.execute("""
            SELECT SUM(hours_day + hours_night)
            FROM work_hours
            WHERE user_id=? AND project_id=? 
              AND date BETWEEN date('now','weekday 0','-6 days') AND date('now','weekday 0')
        """, (user[0], p_id))
        week_hours = db.fetchone()[0] or 0
        total_hours_week += week_hours

        db.execute("""
            SELECT SUM(hours_day + hours_night)
            FROM work_hours
            WHERE user_id=? AND project_id=? 
              AND strftime('%Y-%m', date) = strftime('%Y-%m', 'now')
        """, (user[0], p_id))
        month_hours = db.fetchone()[0] or 0
        total_hours_month += month_hours

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Stundas šonedēļ", total_hours_week)
    with col2:
        st.metric("Stundas šomēnes", total_hours_month)
    with col3:
        st.metric("Aktīvais projekts", active_project)

    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

    db.execute("""
        SELECT strftime('%w', date) AS diena, SUM(hours_day + hours_night)
        FROM work_hours
        WHERE user_id=? AND date BETWEEN date('now','weekday 0','-6 days') AND date('now','weekday 0')
        GROUP BY diena
    """, (user[0],))
    data = db.fetchall()

    if data:
        days_map = {"1":"P", "2":"O", "3":"T", "4":"C", "5":"Pk", "6":"Se", "0":"Sv"}
        df = pd.DataFrame({
            "Diena": [days_map.get(str(d[0]), "?") for d in data],
            "Stundas": [d[1] for d in data]
        })
        st.bar_chart(df.set_index("Diena"))

def manager_dashboard(user):
    st.markdown('<h1 class="gradient-header">📊 Manager Dashboard</h1>', unsafe_allow_html=True)

    
    db.execute("SELECT COUNT(*) FROM projects")
    active_projects = db.fetchone()[0]

    db.execute("SELECT COUNT(*) FROM users WHERE role='worker'")
    total_workers = db.fetchone()[0]

    db.execute("SELECT COUNT(*) FROM invoices WHERE created_at IS NULL")
    pending_invoices = db.fetchone()[0]

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Aktīvie projekti", active_projects)
    with col2:
        st.metric("Darbinieki", total_workers)
    with col3:
        st.metric("Neapstiprināti rēķini", pending_invoices)

    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

    
    st.subheader("💰 Izmaksu sadalījums pa projektiem (šomēnes)")
    
    # get data
    db.execute("""
        SELECT p.name,
               (SELECT SUM(um.quantity * m.price) 
                FROM usage_materials um 
                JOIN materials m ON um.material_id = m.id 
                WHERE um.project_id = p.id 
                AND strftime('%Y-%m', um.date) = strftime('%Y-%m', 'now')) as material_cost,
               (SELECT SUM(wh.hours_day * ? + wh.hours_night * ?) 
                FROM work_hours wh 
                WHERE wh.project_id = p.id 
                AND strftime('%Y-%m', wh.date) = strftime('%Y-%m', 'now')) as hours_cost,
               (SELECT SUM(tu.liters * tu.price_per_liter) 
                FROM transport_usage tu 
                WHERE tu.project_id = p.id 
                AND strftime('%Y-%m', tu.date) = strftime('%Y-%m', 'now')) as transport_cost
        FROM projects p
        WHERE p.id IN (SELECT project_id FROM user_projects WHERE user_id = ?)
    """, (DAY_RATE, NIGHT_RATE, user[0]))
    
    data = db.fetchall()
    
    if data:
        
        projects = []
        materials = []
        hours = []
        transports = []
        
        for row in data:
            projects.append(row[0])
            materials.append(row[1] or 0)
            hours.append(row[2] or 0)
            transports.append(row[3] or 0)
        
        df = pd.DataFrame({
            "Projekts": projects,
            "Materiāli": materials,
            "Darba stundas": hours,
            "Transports": transports
        })
        

        st.bar_chart(df.set_index("Projekts"))
        
    
        total_materials = sum(materials)
        total_hours = sum(hours)
        total_transport = sum(transports)
        total_all = total_materials + total_hours + total_transport
        
        st.success(f"""
        **Kopējās izmaksas šomēnes:** {total_all:.2f} €
        - Materiāli: {total_materials:.2f} €
        - Darba stundas: {total_hours:.2f} €
        - Transports: {total_transport:.2f} €
        """)
        
        
        with st.expander("📋 Detalizēts izmaksu sadalījums"):
            detailed_df = pd.DataFrame({
                "Projekts": projects,
                "Materiāli (€)": [f"{m:.2f}" for m in materials],
                "Stundas (€)": [f"{h:.2f}" for h in hours],
                "Transports (€)": [f"{t:.2f}" for t in transports],
                "Kopā (€)": [f"{m + h + t:.2f}" for m, h, t in zip(materials, hours, transports)]
            })
            st.dataframe(detailed_df, use_container_width=True)
    else:
        st.info("Nav datu šim mēnesim")
        
        
        with st.expander("ℹ️ Kāpēc nav datu?"):
            st.markdown("""
            Iespējamie iemesli:
            - Šomēnes vēl nav reģistrētas darba stundas
            - Šomēnes vēl nav pievienoti materiāli
            - Šomēnes vēl nav reģistrēts transports
            
            Dati parādīsies automātiski, kad tiks veikti pirmie ieraksti.
            """)
            
            
def admin_dashboard():
    st.markdown('<h1 class="gradient-header">📊 Admin Dashboard</h1>', unsafe_allow_html=True)

   
    db.execute("SELECT COUNT(*) FROM users")
    total_users = db.fetchone()[0]

    db.execute("SELECT COUNT(*) FROM projects")
    total_projects = db.fetchone()[0]

    db.execute("SELECT SUM(hours_day + hours_night) FROM work_hours")
    total_hours = db.fetchone()[0] or 0

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Lietotāji", total_users)
    with col2:
        st.metric("Projekti", total_projects)
    with col3:
        st.metric("Stundas kopā", f"{total_hours:.0f}")

    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)


    st.subheader("👥 Aktīvie lietotāji pēdējos 6 mēnešos")
    
    db.execute("""
        SELECT strftime('%Y-%m', date) as month, 
               COUNT(DISTINCT user_id) as active_users
        FROM work_hours
        WHERE date > date('now', '-6 months')
        GROUP BY month
        ORDER BY month
    """)
    data = db.fetchall()
    
    if data:
        df = pd.DataFrame(data, columns=["Mēnesis", "Aktīvie lietotāji"])
        st.bar_chart(df.set_index("Mēnesis"))
        
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Vidēji mēnesī", f"{sum([d[1] for d in data])/len(data):.0f}")
        with col2:
            st.metric("Maksimums", f"{max([d[1] for d in data])}")
        with col3:
            st.metric("Minimums", f"{min([d[1] for d in data])}")
    else:
        st.info("Nav datu par aktivitāti")
    

# UI FUNCTIONS
def add_material_ui(user, project_id):
    st.markdown("### 📦 Materiāli")
    db.execute("SELECT id, name, unit, price FROM materials")
    materials = db.fetchall()
    mat_options = {f"{m[1]} ({m[2]}) - {m[3]}€/unit": m[0] for m in materials}

    mat_sel = st.selectbox("Izvēlies materiālu", list(mat_options.keys()), key=f"mat_{project_id}")
    qty = st.number_input("Daudzums", min_value=0.0, key=f"qty_{project_id}")

    if st.button("Pievienot materiālu", key=f"btn_mat_{project_id}"):
        db.execute("""INSERT INTO usage_materials 
                      (user_id, material_id, quantity, project_id, source, date) 
                      VALUES (?,?,?,?,?,?)""",
                   (user[0], mat_options[mat_sel], qty, project_id, "worker", st.session_state.active_work_date))
        conn.commit()
        st.success("Materiāls pievienots!")

def add_hours_ui(user, project_id):
    st.markdown("### ⏱ Darba stundas")
    hours_day = st.number_input("Dienas stundas", min_value=0.0, key=f"day_{project_id}")
    hours_night = st.number_input("Nakts stundas", min_value=0.0, key=f"night_{project_id}")

    if st.button("Pievienot stundas", key=f"btn_hours_{project_id}"):
        db.execute("""INSERT INTO work_hours 
                      (user_id, project_id, date, hours_day, hours_night)
                      VALUES (?,?,?,?,?)""",
                   (user[0], project_id, st.session_state.active_work_date, hours_day, hours_night))
        conn.commit()
        st.success("Stundas pievienotas!")

def add_transport_ui(user, project_id):
    st.markdown("### 🚗 Transports")
    liters = st.number_input("Patērētie litri", min_value=0.0, key=f"liters_{project_id}")
    price = st.number_input("Cena par litru (€)", min_value=0.0, key=f"price_{project_id}")

    if st.button("Pievienot transporta ierakstu", key=f"btn_trans_{project_id}"):
        db.execute("""INSERT INTO transport_usage
                      (user_id, project_id, liters, price_per_liter, date)
                      VALUES (?,?,?,?,?)""",
                   (user[0], project_id, liters, price, st.session_state.active_work_date))
        conn.commit()
        st.success("Transporta ieraksts pievienots!")

#LOGIN SECTION 
if not st.session_state.logged_in:
    # 
    st.markdown("""
    <div class="login-container">
        <div class="login-card">
            <h1>
                <span>🏗️</span> Projekta Sistēma
            </h1>
            <div class="subtitle">Lūdzu, pieslēdzieties sistēmai</div>
    """, unsafe_allow_html=True)
    
    # Streamlit elements 
    username = st.text_input("Lietotājvārds", placeholder="Ievadiet lietotājvārdu", key="login_username")
    password = st.text_input("Parole", type="password", placeholder="Ievadiet paroli", key="login_password")
    
    if st.button("Pieslēgties", key="login_button", width='stretch'):
   
        db.execute("SELECT id, username, password, role FROM users WHERE username=?", (username,))
        user = db.fetchone()
        
        if user and verify_password(password, user[2]):  # user[2] is the password hash
            st.session_state.logged_in = True
            st.session_state.user = user
            st.rerun()
        else:
            st.error("Nepareizs lietotājvārds vai parole")
    

    st.markdown("""
            <div class="login-footer">
                © 2026 Projekta Sistēma
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.stop()

#MAIN APP SECTION 
else:
    user = st.session_state.user
    
    # Sidebar
    with st.sidebar:
        
        sidebar_header(user)
        
        # Get navigation menu
        menu_items = navigation_menu(user[3])
        
        st.markdown('<hr style="border-color: #374151;">', unsafe_allow_html=True)
        
     
        if isinstance(menu_items, dict):
            for label, icon in menu_items.items():
                if st.button(
                    f"{icon} {label}", 
                    key=f"nav_{label}", 
                    width='stretch'
                ):
                    st.session_state.current_page = label
                    st.rerun()
        else:
            # Simple list fallback
            for label in menu_items:
                if st.button(
                    label, 
                    key=f"nav_{label}", 
                    use_container_width=True
                ):
                    st.session_state.current_page = label
                    st.rerun()
        
        if st.button("🚪 Iziet", width='stretch'):
            st.session_state.logged_in = False
            st.rerun()
    
    # Main content area based on role and selected page
    if user[3] == "admin":
        if st.session_state.current_page == "Dashboard":
            admin_dashboard()
        
        elif st.session_state.current_page == "Lietotāji":
            st.subheader("👤 Lietotāju pārvaldība")
            
            # FILTers
            with st.expander("🔍 Filtrēt lietotājus", expanded=False):
                col1, col2, col3 = st.columns(3)
                with col1:
                    filter_name = st.text_input("Vārds", placeholder="Meklēt pēc vārda...")
                with col2:
                    filter_role = st.selectbox("Loma", ["Visi", "admin", "manager", "worker"])
                with col3:
                    filter_id = st.text_input("ID", placeholder="Meklēt pēc ID...")

            with st.expander("➕ Pievienot jaunu lietotāju", expanded=True):
                new_user = st.text_input("Lietotājvārds")
                new_pass = st.text_input("Parole", type="password")
                new_role = st.selectbox("Loma", ["admin", "manager", "worker"])

                if st.button("Pievienot", width='stretch'):
                    if new_user and new_pass:
                        try:
                            hashed_password = hash_password(new_pass)
                            db.execute("INSERT INTO users (username, password, role) VALUES (?,?,?)",
                                       (new_user, hashed_password, new_role))
                            conn.commit()
                            st.success("Lietotājs pievienots!")
                            st.rerun()
                        except sqlite3.IntegrityError:
                            st.error("Lietotājvārds jau eksistē!")

            st.markdown("### 📋 Esošie lietotāji")
            
           
            query = "SELECT id, username, role FROM users WHERE 1=1"
            params = []
            
            if filter_name:
                query += " AND username LIKE ?"
                params.append(f"%{filter_name}%")
            if filter_role != "Visi":
                query += " AND role = ?"
                params.append(filter_role)
            if filter_id:
                query += " AND id = ?"
                params.append(filter_id)
                
            query += " ORDER BY id"
            
            db.execute(query, params)
            users = db.fetchall()
            
    
            st.caption(f"Atrasti {len(users)} lietotāji")

            for u in users:
                with st.container():
                
                    col1, col2, col3, col4, col5 = st.columns([1, 2, 2, 1, 1])
                    
                    col1.write(f"**ID:** {u[0]}")
                    col2.write(f"**Lietotājs:** {u[1]}")
                    
                    new_role = col3.selectbox(
                        "Loma",
                        ["admin", "manager", "worker"],
                        index=["admin", "manager", "worker"].index(u[2]),
                        key=f"role_{u[0]}",
                        label_visibility="collapsed"
                    )

                    if col4.button("💾", key=f"save_{u[0]}", help="Saglabāt izmaiņas"):
                        db.execute("UPDATE users SET role=? WHERE id=?", (new_role, u[0]))
                        conn.commit()
                        st.success("Loma atjaunināta!")
                        st.rerun()
                    
                    if col5.button("🗑️", key=f"delete_{u[0]}", help="Dzēst lietotāju"):
                        if u[1] == "admin" and u[0] == 1:
                            st.error("Nevar dzēst galveno administratoru!")
                        else:
                            st.session_state[f"confirm_delete_user_{u[0]}"] = True
                    
                    if st.session_state.get(f"confirm_delete_user_{u[0]}", False):
                        st.warning(f"Vai tiešām vēlaties dzēst lietotāju '{u[1]}'?")
                        col_yes, col_no = st.columns(2)
                        with col_yes:
                            if st.button("Jā, dzēst", key=f"confirm_yes_{u[0]}"):
                                try:
                                    db.execute("SELECT COUNT(*) FROM user_projects WHERE user_id=?", (u[0],))
                                    project_count = db.fetchone()[0]
                                    
                                    if project_count > 0:
                                        db.execute("DELETE FROM user_projects WHERE user_id=?", (u[0],))
                                    
                                    db.execute("DELETE FROM users WHERE id=?", (u[0],))
                                    conn.commit()
                                    st.success(f"Lietotājs '{u[1]}' dzēsts!")
                                    st.session_state[f"confirm_delete_user_{u[0]}"] = False
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Kļūda dzēšot lietotāju: {e}")
                                    st.session_state[f"confirm_delete_user_{u[0]}"] = False
                        
                        with col_no:
                            if st.button("Nē, atcelt", key=f"confirm_no_{u[0]}"):
                                st.session_state[f"confirm_delete_user_{u[0]}"] = False
                                st.rerun()
                    
                    st.divider()

        elif st.session_state.current_page == "Projekti":
            st.subheader("🏗 Projektu pārvaldība")
            
            with st.expander("🔍 Filtrēt projektus", expanded=False):
                col1, col2, col3 = st.columns(3)
                with col1:
                    filter_proj_name = st.text_input("Nosaukums", placeholder="Meklēt pēc nosaukuma...")
                with col2:
                    filter_client = st.text_input("Klients", placeholder="Meklēt pēc klienta...")
                with col3:
                    filter_proj_id = st.text_input("ID", placeholder="Meklēt pēc ID...")

            with st.expander("➕ Pievienot projektu", expanded=True):
                proj_name = st.text_input("Nosaukums")
                client_name = st.text_input("Klients")
                address = st.text_input("Adrese")

                if st.button("Pievienot projektu", width='stretch'):
                    if proj_name:
                        db.execute(
                            "INSERT INTO projects (name, client_name, address) VALUES (?,?,?)",
                            (proj_name, client_name, address)
                        )
                        conn.commit()
                        st.success("Projekts pievienots!")
                        st.rerun()

            st.markdown("### 📋 Esošie projekti")
            
            query = "SELECT id, name, client_name, address FROM projects WHERE 1=1"
            params = []
            
            if filter_proj_name:
                query += " AND name LIKE ?"
                params.append(f"%{filter_proj_name}%")
            if filter_client:
                query += " AND client_name LIKE ?"
                params.append(f"%{filter_client}%")
            if filter_proj_id:
                query += " AND id = ?"
                params.append(filter_proj_id)
                
            query += " ORDER BY id"
            
            db.execute(query, params)
            projects = db.fetchall()
            
            st.caption(f"Atrasti {len(projects)} projekti")

            for p in projects:
                with st.container():
                    col1, col2, col3, col4 = st.columns([1, 3, 3, 1])
                    
                    col1.write(f"**ID:** {p[0]}")
                    col2.write(f"**Nosaukums:** {p[1]}")
                    col3.write(f"**Klients:** {p[2]}")
                    
                    if col4.button("🗑️", key=f"delete_project_{p[0]}", help="Dzēst projektu"):
                        st.session_state[f"confirm_delete_project_{p[0]}"] = True
                    
                    if st.session_state.get(f"confirm_delete_project_{p[0]}", False):
                        st.warning(f"Vai tiešām vēlaties dzēst projektu '{p[1]}'?")
                        
                        db.execute("SELECT COUNT(*) FROM user_projects WHERE project_id=?", (p[0],))
                        user_count = db.fetchone()[0]
                        
                        db.execute("SELECT COUNT(*) FROM usage_materials WHERE project_id=?", (p[0],))
                        material_count = db.fetchone()[0]
                        
                        db.execute("SELECT COUNT(*) FROM work_hours WHERE project_id=?", (p[0],))
                        hours_count = db.fetchone()[0]
                        
                        db.execute("SELECT COUNT(*) FROM transport_usage WHERE project_id=?", (p[0],))
                        transport_count = db.fetchone()[0]
                        
                        db.execute("SELECT COUNT(*) FROM invoices WHERE project_id=?", (p[0],))
                        invoice_count = db.fetchone()[0]
                        
                        if user_count > 0 or material_count > 0 or hours_count > 0 or transport_count > 0 or invoice_count > 0:
                            st.error(f"⚠️ Projektam ir piesaistīti dati:")
                            if user_count > 0:
                                st.write(f"- {user_count} lietotāju piesaistes")
                            if material_count > 0:
                                st.write(f"- {material_count} materiālu ieraksti")
                            if hours_count > 0:
                                st.write(f"- {hours_count} darba stundu ieraksti")
                            if transport_count > 0:
                                st.write(f"- {transport_count} transporta ieraksti")
                            if invoice_count > 0:
                                st.write(f"- {invoice_count} rēķini")
                            
                            st.warning("Dzēšot projektu, visi šie dati tiks dzēsti!")
                        
                        col_yes, col_no = st.columns(2)
                        with col_yes:
                            if st.button("Jā, dzēst visu", key=f"confirm_yes_project_{p[0]}"):
                                try:
                                    db.execute("DELETE FROM user_projects WHERE project_id=?", (p[0],))
                                    db.execute("DELETE FROM usage_materials WHERE project_id=?", (p[0],))
                                    db.execute("DELETE FROM work_hours WHERE project_id=?", (p[0],))
                                    db.execute("DELETE FROM transport_usage WHERE project_id=?", (p[0],))
                                    db.execute("DELETE FROM invoices WHERE project_id=?", (p[0],))
                                    db.execute("DELETE FROM projects WHERE id=?", (p[0],))
                                    conn.commit()
                                    st.success(f"Projekts '{p[1]}' un visi saistītie dati dzēsti!")
                                    st.session_state[f"confirm_delete_project_{p[0]}"] = False
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Kļūda dzēšot projektu: {e}")
                                    st.session_state[f"confirm_delete_project_{p[0]}"] = False
                        
                        with col_no:
                            if st.button("Nē, atcelt", key=f"confirm_no_project_{p[0]}"):
                                st.session_state[f"confirm_delete_project_{p[0]}"] = False
                                st.rerun()
                    
                    st.divider()

        elif st.session_state.current_page == "Piesaistes":
            st.subheader("🔗 Projekta piesaiste lietotājam")

            db.execute("SELECT id, username FROM users")
            users = db.fetchall()

            db.execute("SELECT id, name FROM projects")
            projects = db.fetchall()

            if not users or not projects:
                st.warning("Nav lietotāju vai projektu")
                st.stop()

            user_map = {u[1]: u[0] for u in users}
            project_map = {p[1]: p[0] for p in projects}

            col1, col2 = st.columns(2)
            with col1:
                sel_user = st.selectbox("Lietotājs", list(user_map.keys()))
            with col2:
                sel_project = st.selectbox("Projekts", list(project_map.keys()))

            if st.button("Piesaistīt projektu", width='stretch'):
                db.execute(
                    "INSERT OR IGNORE INTO user_projects (user_id, project_id) VALUES (?,?)",
                    (user_map[sel_user], project_map[sel_project])
                )
                conn.commit()
                st.success("Projekts piesaistīts!")
                st.rerun()

    elif user[3] == "manager":
        if st.session_state.current_page == "Dashboard":
            manager_dashboard(user)

        elif st.session_state.current_page == "Rēķini":
            st.subheader("📄 Rēķini")
            
            tab1, tab2 = st.tabs(["📋 Rēķinu vēsture", "➕ Jauns rēķins"])
            
            with tab1:
                st.markdown("### 📋 Iepriekšējie rēķini")
                
                with st.expander("🔍 Filtrēt rēķinus", expanded=False):
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        filter_date_from = st.date_input("No", value=None, key="filter_date_from")
                    with col2:
                        filter_date_to = st.date_input("Līdz", value=None, key="filter_date_to")
                    with col3:
                        db.execute("SELECT DISTINCT u.username FROM users u JOIN user_projects up ON u.id = up.user_id WHERE up.project_id IN (SELECT project_id FROM user_projects WHERE user_id = ?)", (user[0],))
                        user_list = [u[0] for u in db.fetchall()]
                        filter_inv_user = st.selectbox("Lietotājs", ["Visi"] + user_list, key="filter_inv_user")
                    
                    col4, col5, col6 = st.columns(3)
                    with col4:
                        db.execute("SELECT p.id, p.name FROM projects p JOIN user_projects up ON p.id = up.project_id WHERE up.user_id = ?", (user[0],))
                        project_list = [p[1] for p in db.fetchall()]
                        filter_inv_project = st.selectbox("Projekts", ["Visi"] + project_list, key="filter_inv_project")
                    with col5:
                        filter_inv_id = st.text_input("Rēķina Nr.", placeholder="Meklēt pēc ID...")
                    with col6:
                        filter_min_amount = st.number_input("Summa (€)", min_value=0.0, step=100.0, key="filter_min")
                
                query = """
                    SELECT i.id, i.created_at, u.username, p.name, 
                           (SELECT SUM(um.quantity * m.price) 
                            FROM usage_materials um 
                            JOIN materials m ON um.material_id = m.id 
                            WHERE um.user_id = i.user_id AND um.project_id = i.project_id 
                            AND um.date BETWEEN date(i.created_at, '-30 days') AND i.created_at) as material_cost,
                           (SELECT SUM(wh.hours_day * ? + wh.hours_night * ?) 
                            FROM work_hours wh 
                            WHERE wh.user_id = i.user_id AND wh.project_id = i.project_id 
                            AND wh.date BETWEEN date(i.created_at, '-30 days') AND i.created_at) as hours_cost,
                           (SELECT SUM(tu.liters * tu.price_per_liter) 
                            FROM transport_usage tu 
                            WHERE tu.user_id = i.user_id AND tu.project_id = i.project_id 
                            AND tu.date BETWEEN date(i.created_at, '-30 days') AND i.created_at) as transport_cost
                    FROM invoices i
                    JOIN users u ON i.user_id = u.id
                    JOIN projects p ON i.project_id = p.id
                    WHERE i.project_id IN (SELECT project_id FROM user_projects WHERE user_id = ?)
                """
                params = [DAY_RATE, NIGHT_RATE, user[0]]
                
                if filter_date_from:
                    query += " AND date(i.created_at) >= ?"
                    params.append(filter_date_from)
                if filter_date_to:
                    query += " AND date(i.created_at) <= ?"
                    params.append(filter_date_to)
                if filter_inv_user and filter_inv_user != "Visi":
                    query += " AND u.username = ?"
                    params.append(filter_inv_user)
                if filter_inv_project and filter_inv_project != "Visi":
                    query += " AND p.name = ?"
                    params.append(filter_inv_project)
                if filter_inv_id:
                    query += " AND i.id = ?"
                    params.append(int(filter_inv_id) if filter_inv_id.isdigit() else 0)
                
                query += " ORDER BY i.created_at DESC"
                
                db.execute(query, params)
                invoices = db.fetchall()
                
                if invoices:
                    invoice_data = []
                    filtered_invoices = []
                    
                    for inv in invoices:
                        total = (inv[4] or 0) + (inv[5] or 0) + (inv[6] or 0)
                        
                        if filter_min_amount and total < filter_min_amount:
                            continue
                            
                        invoice_data.append({
                            "Nr.": inv[0],
                            "Datums": inv[1],
                            "Lietotājs": inv[2],
                            "Projekts": inv[3],
                            "Summa (€)": f"{total:.2f}"
                        })
                        filtered_invoices.append(inv)
                    
                    st.caption(f"Atrasti {len(invoice_data)} rēķini")
                    df = pd.DataFrame(invoice_data)
                    st.dataframe(df, use_container_width=True)
                    
                    if filtered_invoices:
                        st.markdown("### 📄 Rēķina detalizācija")
                        selected_invoice = st.selectbox(
                            "Izvēlies rēķinu", 
                            options=[f"{inv[0]} - {inv[1]} - {inv[2]}" for inv in filtered_invoices],
                            key="invoice_history_select"
                        )
                        
                        if selected_invoice:
                            inv_id = int(selected_invoice.split(" - ")[0])
                            
                            db.execute("""
                                SELECT u.username, p.name, i.created_at
                                FROM invoices i
                                JOIN users u ON i.user_id = u.id
                                JOIN projects p ON i.project_id = p.id
                                WHERE i.id = ?
                            """, (inv_id,))
                            inv_details = db.fetchone()
                            
                            if inv_details:
                                st.markdown(f"""
                                **Rēķins Nr. {inv_id}**  
                                **Datums:** {inv_details[2]}  
                                **Lietotājs:** {inv_details[0]}  
                                **Projekts:** {inv_details[1]}  
                                """)
                                
                                st.markdown("#### 📦 Materiāli")
                                db.execute("""
                                    SELECT m.name, SUM(um.quantity), m.price
                                    FROM usage_materials um
                                    JOIN materials m ON um.material_id = m.id
                                    WHERE um.user_id = (SELECT user_id FROM invoices WHERE id = ?)
                                    AND um.project_id = (SELECT project_id FROM invoices WHERE id = ?)
                                    AND um.date BETWEEN date((SELECT created_at FROM invoices WHERE id = ?), '-30 days') 
                                    AND (SELECT created_at FROM invoices WHERE id = ?)
                                    GROUP BY m.id
                                """, (inv_id, inv_id, inv_id, inv_id))
                                
                                materials = db.fetchall()
                                if materials:
                                    mat_df = pd.DataFrame(materials, columns=["Materiāls", "Daudzums", "Cena"])
                                    st.dataframe(mat_df, use_container_width=True)
                                else:
                                    st.info("Nav materiālu")
                else:
                    st.info("Nav izveidotu rēķinu")
                    
            # invoice generation
            
            with tab2:
                st.markdown("### ➕ Rēķina ģenerēšana")
                
                db.execute("""
                SELECT p.id, p.name
                FROM projects p
                JOIN user_projects up ON p.id = up.project_id
                WHERE up.user_id = ?
                """, (user[0],))
                projects = db.fetchall()

                project_map = {p[1]: p[0] for p in projects}
                if not project_map:
                    st.warning("Nav pieejamu projektu")
                    st.stop()

                project_name = st.selectbox("Izvēlies projektu", list(project_map.keys()))
                project_id = project_map[project_name]

                # Get users for this project
                db.execute("""
                SELECT u.id, u.username
                FROM users u
                JOIN user_projects up ON u.id = up.user_id
                WHERE up.project_id = ?
                """, (project_id,))
                users = db.fetchall()

                if users:
                    user_options = [u[1] for u in users]
                    selected_users = st.multiselect(
                        "Izvēlies lietotāju(s) (var izvēlēties vairākus)", 
                        user_options,
                        help="Izvēlies vienu vai vairākus lietotājus, par kuriem vēlies ģenerēt rēķinu"
                    )
                    
                    # Date range
                    col1, col2 = st.columns(2)
                    with col1:
                        start_date = st.date_input("Sākuma datums", date.today())
                    with col2:
                        end_date = st.date_input("Beigu datums", date.today())

                    if selected_users:
                        selected_user_ids = [u[0] for u in users if u[1] in selected_users]
                        
                        placeholders = ','.join('?' * len(selected_user_ids))
                        db.execute(f"""
                            SELECT m.name, SUM(um.quantity), m.price
                            FROM usage_materials um
                            JOIN materials m ON um.material_id = m.id
                            WHERE um.user_id IN ({placeholders})
                            AND um.project_id = ?
                            AND um.date BETWEEN ? AND ?
                            GROUP BY m.id
                        """, selected_user_ids + [project_id, start_date, end_date])
                        materials_data = db.fetchall()
                        
                        db.execute(f"""
                            SELECT SUM(hours_day), SUM(hours_night)
                            FROM work_hours
                            WHERE user_id IN ({placeholders})
                            AND project_id = ?
                            AND date BETWEEN ? AND ?
                        """, selected_user_ids + [project_id, start_date, end_date])
                        day_hours, night_hours = db.fetchone()
                        day_hours = day_hours or 0
                        night_hours = night_hours or 0

                        db.execute(f"""
                            SELECT SUM(liters), AVG(price_per_liter)
                            FROM transport_usage
                            WHERE user_id IN ({placeholders})
                            AND project_id = ?
                            AND date BETWEEN ? AND ?
                        """, selected_user_ids + [project_id, start_date, end_date])
                        liters, avg_price = db.fetchone()
                        liters = liters or 0
                        avg_price = avg_price or 0

                        # Create summary
                        rows = []
                        for name, qty, price in materials_data:
                            rows.append({
                                "Tips": "Materiāls",
                                "Nosaukums": name,
                                "Daudzums": qty,
                                "Summa (€)": qty * price
                            })

                        rows.append({
                            "Tips": "Darbs",
                            "Nosaukums": "Darba stundas",
                            "Daudzums": day_hours + night_hours,
                            "Summa (€)": day_hours * DAY_RATE + night_hours * NIGHT_RATE
                        })

                        rows.append({
                            "Tips": "Transports",
                            "Nosaukums": "Degviela",
                            "Daudzums": liters,
                            "Summa (€)": liters * avg_price
                        })

                        df = pd.DataFrame(rows)
                        st.dataframe(df, use_container_width=True)

                        # Calculate totals
                        mat_total = sum(row["Summa (€)"] for row in rows if row["Tips"] == "Materiāls")
                        hours_total = day_hours * DAY_RATE + night_hours * NIGHT_RATE
                        trans_total = liters * avg_price
                        total = mat_total + hours_total + trans_total

                        st.success(f"""
                        **Kopsavilkums:**
                        - Atlasīti lietotāji: {', '.join(selected_users)}
                        - Materiāli: {mat_total:.2f} €
                        - Darba stundas: {hours_total:.2f} €
                        - Transports: {trans_total:.2f} €
                        - **KOPĀ: {total:.2f} €**
                        """)

                        # PDF EXPORT BUTTON
                        if st.button("📥 Eksportēt PDF", key="export_pdf", width='stretch'):
                            try:
                                if not materials_data and day_hours == 0 and night_hours == 0 and not liters:
                                    st.warning("Nav datu eksportēšanai!")
                                else:
                                    db.execute(
                                        "INSERT INTO invoices (user_id, project_id, created_at) VALUES (?,?,?)",
                                        (selected_user_ids[0], project_id, date.today().isoformat())
                                    )
                                    conn.commit()
                                    invoice_id = db.lastrowid
                                    
                                    filename = f"rekins_{invoice_id}.pdf"
                                    
                                    result = generate_invoice_pdf(
                                        invoice_id,
                                        selected_user_ids[0],  
                                        project_id,
                                        start_date,
                                        end_date,
                                        filename=filename
                                    )
                                    
                                    if result and os.path.exists(filename):
                                        file_size = os.path.getsize(filename)
                                        st.success(f"PDF fails izveidots! Izmērs: {file_size} baiti")
                                        
                                        with open(filename, "rb") as f:
                                            pdf_data = f.read()
                                            st.download_button(
                                                "📥 Lejupielādēt PDF",
                                                pdf_data,
                                                file_name=filename,
                                                mime="application/pdf",
                                                key="download_pdf"
                                            )
                                    else:
                                        st.error("Neizdevās izveidot PDF failu!")
                            except Exception as e:
                                st.error(f"Kļūda: {e}")
                    else:
                        st.info("Lūdzu, izvēlies vismaz vienu lietotāju")
                else:
                    st.info("Šim projektam nav piesaistītu lietotāju")

    elif user[3] == "worker":  
        # Worker section
        if "active_work_date" not in st.session_state:
            st.session_state.active_work_date = date.today()

        st.session_state.active_work_date = st.date_input(
            "📅 Darba datums",
            value=st.session_state.active_work_date
        )
        st.caption(f"Aktīvais datums: {st.session_state.active_work_date}")
        st.divider()

        db.execute("""
            SELECT p.id, p.name
            FROM projects p
            JOIN user_projects up ON p.id = up.project_id
            WHERE up.user_id = ?
        """, (user[0],))
        projects = db.fetchall()
        
        if not projects:
            st.warning("Nav piesaistītu projektu")
            st.stop()

        project_map = {p[1]: p[0] for p in projects}
        project_name = st.selectbox("Izvēlies projektu", list(project_map.keys()))
        project_id = project_map[project_name]

        if st.session_state.current_page == "Dashboard":
            st.markdown('<h1 class="gradient-header">📊 Worker Dashboard</h1>', unsafe_allow_html=True)

            total_hours_week = 0
            total_hours_month = 0
            total_materials_week = 0
            total_materials_month = 0
            active_project = projects[0][1] if projects else "Nav"

            for p_id, p_name in projects:
                db.execute("""
                    SELECT SUM(hours_day + hours_night)
                    FROM work_hours
                    WHERE user_id=? AND project_id=? 
                      AND date BETWEEN date('now','weekday 0','-6 days') AND date('now','weekday 0')
                """, (user[0], p_id))
                week_hours = db.fetchone()[0] or 0
                total_hours_week += week_hours

                db.execute("""
                    SELECT SUM(hours_day + hours_night)
                    FROM work_hours
                    WHERE user_id=? AND project_id=? 
                      AND strftime('%Y-%m', date) = strftime('%Y-%m', 'now')
                """, (user[0], p_id))
                month_hours = db.fetchone()[0] or 0
                total_hours_month += month_hours
                
                db.execute("""
                    SELECT SUM(quantity)
                    FROM usage_materials
                    WHERE user_id=? AND project_id=? 
                      AND date BETWEEN date('now','weekday 0','-6 days') AND date('now','weekday 0')
                """, (user[0], p_id))
                week_materials = db.fetchone()[0] or 0
                total_materials_week += week_materials
                
                db.execute("""
                    SELECT SUM(quantity)
                    FROM usage_materials
                    WHERE user_id=? AND project_id=? 
                      AND strftime('%Y-%m', date) = strftime('%Y-%m', 'now')
                """, (user[0], p_id))
                month_materials = db.fetchone()[0] or 0
                total_materials_month += month_materials

            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Stundas šonedēļ", total_hours_week)
            with col2:
                st.metric("Stundas šomēnes", total_hours_month)
            with col3:
                st.metric("Materiāli šonedēļ", f"{total_materials_week} vien.")
            with col4:
                st.metric("Aktīvais projekts", active_project)

            st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

            tab1, tab2, tab3 = st.tabs(["📊 Stundu grafiks", "📦 Mani materiāli", "⏱ Manas stundas"])
            
            with tab1:
                db.execute("""
                    SELECT strftime('%w', date) AS diena, SUM(hours_day + hours_night)
                    FROM work_hours
                    WHERE user_id=? AND date BETWEEN date('now','weekday 0','-6 days') AND date('now','weekday 0')
                    GROUP BY diena
                """, (user[0],))
                data = db.fetchall()

                if data:
                    days_map = {"1":"P", "2":"O", "3":"T", "4":"C", "5":"Pk", "6":"Se", "0":"Sv"}
                    df = pd.DataFrame({
                        "Diena": [days_map.get(str(d[0]), "?") for d in data],
                        "Stundas": [d[1] for d in data]
                    })
                    st.bar_chart(df.set_index("Diena"))
                else:
                    st.info("Nav datu stundu grafikam")
            
            with tab2:
                st.markdown("### 📦 Manu materiālu vēsture")
                
                with st.expander("🔍 Filtrēt materiālus", expanded=False):
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        filter_mat_from = st.date_input("No datuma", value=date.today().replace(day=1), key="worker_mat_from")
                    with col2:
                        filter_mat_to = st.date_input("Līdz datumam", value=date.today(), key="worker_mat_to")
                    with col3:
                        filter_project = st.selectbox("Projekts", ["Visi"] + [p[1] for p in projects], key="worker_mat_project")
                    
                    col4, col5, col6 = st.columns(3)
                    with col4:
                        filter_material = st.text_input("Materiāla nosaukums", placeholder="Meklēt...", key="worker_mat_name")
                    with col5:
                        filter_min_qty = st.number_input("Min. daudzums", min_value=0.0, step=1.0, key="worker_min_qty")
                    with col6:
                        filter_max_qty = st.number_input("Max. daudzums", min_value=0.0, step=1.0, key="worker_max_qty")
                
                query = """
                    SELECT um.date, p.name, m.name, um.quantity, m.unit, m.price, (um.quantity * m.price) as total_cost
                    FROM usage_materials um
                    JOIN materials m ON um.material_id = m.id
                    JOIN projects p ON um.project_id = p.id
                    WHERE um.user_id = ?
                """
                params = [user[0]]
                
                if filter_mat_from:
                    query += " AND um.date >= ?"
                    params.append(filter_mat_from.isoformat())
                if filter_mat_to:
                    query += " AND um.date <= ?"
                    params.append(filter_mat_to.isoformat())
                if filter_project and filter_project != "Visi":
                    proj_id = [p[0] for p in projects if p[1] == filter_project][0]
                    query += " AND um.project_id = ?"
                    params.append(proj_id)
                if filter_material:
                    query += " AND m.name LIKE ?"
                    params.append(f"%{filter_material}%")
                
                query += " ORDER BY um.date DESC"
                
                db.execute(query, params)
                material_data = db.fetchall()
                
                if material_data:
                    filtered_data = []
                    for m in material_data:
                        if filter_min_qty and m[3] < filter_min_qty:
                            continue
                        if filter_max_qty and m[3] > filter_max_qty:
                            continue
                        filtered_data.append({
                            "Datums": m[0],
                            "Projekts": m[1],
                            "Materiāls": m[2],
                            "Daudzums": f"{m[3]} {m[4]}",
                            "Cena": f"{m[5]:.2f} €",
                            "Kopā": f"{m[6]:.2f} €"
                        })
                    
                    st.caption(f"Atrasti {len(filtered_data)} materiālu ieraksti")
                    
                    if filtered_data:
                        df = pd.DataFrame(filtered_data)
                        st.dataframe(df, use_container_width=True)
                        
                        st.markdown("### 📊 Materiālu statistika")
                        
                        total_value = sum(float(m["Kopā"].replace(" €", "")) for m in filtered_data)
                        
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Kopējais ierakstu skaits", len(filtered_data))
                        with col2:
                            st.metric("Kopējā materiālu vērtība", f"{total_value:.2f} €")
                        with col3:
                            avg_value = total_value / len(filtered_data) if filtered_data else 0
                            st.metric("Vidējā vērtība", f"{avg_value:.2f} €")
                        
                        st.markdown("#### Materiālu sadalījums pēc daudzuma")
                        material_summary = {}
                        for m in filtered_data:
                            mat_name = m["Materiāls"]
                            qty = float(m["Daudzums"].split()[0])
                            if mat_name in material_summary:
                                material_summary[mat_name] += qty
                            else:
                                material_summary[mat_name] = qty
                        
                        if material_summary:
                            summary_df = pd.DataFrame({
                                "Materiāls": list(material_summary.keys()),
                                "Daudzums": list(material_summary.values())
                            })
                            st.bar_chart(summary_df.set_index("Materiāls"))
                    else:
                        st.info("Nav materiālu, kas atbilst filtrieriem")
                else:
                    st.info("Jums vēl nav pievienotu materiālu")
                    
                    with st.expander("ℹ️ Kā pievienot materiālus?"):
                        st.markdown("""
                        Lai pievienotu materiālus:
                        1. Dodieties uz sadaļu **Materiāli** kreisajā izvēlnē
                        2. Izvēlieties projektu
                        3. Izvēlieties materiālu no saraksta
                        4. Ievadiet daudzumu
                        5. Nospiediet "Pievienot materiālu"
                        
                        Pievienotie materiāli automātiski parādīsies šajā vēsturē.
                        """)
            
            with tab3:
                st.markdown("### ⏱ Manu stundu vēsture")
                
                with st.expander("🔍 Filtrēt stundas", expanded=False):
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        filter_hours_from = st.date_input("No datuma", value=date.today().replace(day=1), key="worker_hours_from")
                    with col2:
                        filter_hours_to = st.date_input("Līdz datumam", value=date.today(), key="worker_hours_to")
                    with col3:
                        filter_hours_project = st.selectbox("Projekts", ["Visi"] + [p[1] for p in projects], key="worker_hours_project")
                
                query = """
                    SELECT wh.date, p.name, wh.hours_day, wh.hours_night, 
                           (wh.hours_day + wh.hours_night) as total_hours,
                           (wh.hours_day * ? + wh.hours_night * ?) as total_cost
                    FROM work_hours wh
                    JOIN projects p ON wh.project_id = p.id
                    WHERE wh.user_id = ?
                """
                params = [DAY_RATE, NIGHT_RATE, user[0]]
                
                if filter_hours_from:
                    query += " AND wh.date >= ?"
                    params.append(filter_hours_from.isoformat())
                if filter_hours_to:
                    query += " AND wh.date <= ?"
                    params.append(filter_hours_to.isoformat())
                if filter_hours_project and filter_hours_project != "Visi":
                    proj_id = [p[0] for p in projects if p[1] == filter_hours_project][0]
                    query += " AND wh.project_id = ?"
                    params.append(proj_id)
                
                query += " ORDER BY wh.date DESC"
                
                db.execute(query, params)
                hours_data = db.fetchall()
                
                if hours_data:
                    hours_list = []
                    for h in hours_data:
                        hours_list.append({
                            "Datums": h[0],
                            "Projekts": h[1],
                            "Dienas stundas": h[2],
                            "Nakts stundas": h[3],
                            "Kopā stundas": h[4],
                            "Izmaksas (€)": f"{h[5]:.2f}"
                        })
                    
                    st.caption(f"Atrasti {len(hours_list)} stundu ieraksti")
                    df = pd.DataFrame(hours_list)
                    st.dataframe(df, use_container_width=True)
                    
                    total_hours = sum(h[4] for h in hours_data)
                    total_cost = sum(h[5] for h in hours_data)
                    total_day = sum(h[2] for h in hours_data)
                    total_night = sum(h[3] for h in hours_data)
                    
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Kopā stundas", total_hours)
                    with col2:
                        st.metric("Dienas stundas", total_day)
                    with col3:
                        st.metric("Nakts stundas", total_night)
                    with col4:
                        st.metric("Kopējās izmaksas", f"{total_cost:.2f} €")
                else:
                    st.info("Jums vēl nav pievienotu stundu")

        elif st.session_state.current_page == "Materiāli":
            add_material_ui(user, project_id)
        elif st.session_state.current_page == "Stundas":
            add_hours_ui(user, project_id)
        elif st.session_state.current_page == "Transports":
            add_transport_ui(user, project_id)
