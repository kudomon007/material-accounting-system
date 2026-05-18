# styles.py
"""
Tumšais režīms visai Projekta Sistēmai
"""

MAIN_STYLES = """
<style>
    /* Modern Color Scheme - DARK MODE */
    :root {
        --primary: #818cf8;
        --primary-dark: #6366f1;
        --secondary: #34d399;
        --danger: #f87171;
        --warning: #fbbf24;
        --dark: #111827;
        --darker: #030712;
        --light: #1f2937;
        --lighter: #374151;
        --gray: #9ca3af;
        --gray-light: #6b7280;
        --gradient-start: #4f46e5;
        --gradient-end: #7c3aed;
        --card-bg: #1f2937;
        --card-border: #374151;
        --text-primary: #f9fafb;
        --text-secondary: #e5e7eb;
        --text-muted: #9ca3af;
    }
    
    /* ===== PAMATA STILI ===== */
    .main {
        background: linear-gradient(135deg, #111827 0%, #1f2937 100%);
        padding: 20px;
        min-height: 100vh;
    }
    
    /* Vispārējie teksta stili */
    body, p, span, div, label, .stMarkdown, .stText {
        color: var(--text-primary) !important;
    }
    
    /* ===== KARTES ===== */
    .custom-card {
        background: var(--card-bg) !important;
        border-radius: 20px;
        padding: 25px;
        box-shadow: 0 10px 40px rgba(0,0,0,0.5);
        margin-bottom: 20px;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        border: 1px solid var(--card-border);
    }
    
    .custom-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 20px 60px rgba(0,0,0,0.7);
    }
    
    /* ===== VIRSRAKSTI ===== */
    .gradient-header {
        background: linear-gradient(135deg, var(--gradient-start) 0%, var(--gradient-end) 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 20px;
    }
    
    h1, h2, h3, h4, h5, h6 {
        color: var(--text-primary) !important;
    }
    
    .subtitle {
        color: var(--text-muted);
        font-size: 1rem;
        margin-bottom: 20px;
    }
    
    /* ===== POGAS ===== */
    .stButton > button {
        background: linear-gradient(135deg, var(--gradient-start) 0%, var(--gradient-end) 100%);
        color: white !important;
        border: none;
        border-radius: 12px;
        padding: 12px 24px;
        font-weight: 600;
        font-size: 16px;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(79, 70, 229, 0.3);
        width: 100%;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(79, 70, 229, 0.5);
    }
    
    .stButton > button:active {
        transform: translateY(0);
    }
    
    /* Sekundārās pogas */
    .secondary-button > button {
        background: transparent;
        color: var(--text-primary) !important;
        border: 2px solid var(--primary);
        box-shadow: none;
    }
    
    .secondary-button > button:hover {
        background: rgba(129, 140, 248, 0.1);
    }
    
    /* ===== IEVADES LAUKI ===== */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stDateInput > div > div > input,
    .stSelectbox > div > div > select {
        border-radius: 12px !important;
        border: 2px solid var(--card-border) !important;
        padding: 12px !important;
        font-size: 16px !important;
        transition: all 0.3s ease !important;
        color: var(--text-primary) !important;
        background: var(--darker) !important;
    }
    
    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus,
    .stDateInput > div > div > input:focus,
    .stSelectbox > div > div > select:focus {
        border-color: var(--primary) !important;
        box-shadow: 0 0 0 3px rgba(129, 140, 248, 0.2) !important;
    }
    
    /* Selectbox dropdown */
    .stSelectbox > div > div > div {
        background: var(--darker) !important;
        color: var(--text-primary) !important;
    }
    
    /* ===== METRIKAS KARTES ===== */
    div[data-testid="metric-container"] {
        background: var(--card-bg) !important;
        padding: 25px !important;
        border-radius: 20px !important;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5) !important;
        border: 1px solid var(--card-border) !important;
        transition: transform 0.3s ease;
    }
    
    div[data-testid="metric-container"]:hover {
        transform: translateY(-5px);
    }
    
    div[data-testid="metric-container"] label {
        color: var(--text-muted) !important;
        font-size: 14px !important;
        text-transform: uppercase !important;
    }
    
    div[data-testid="metric-container"] div {
        color: var(--text-primary) !important;
        font-size: 32px !important;
        font-weight: 700 !important;
    }
    
    /* ===== SĀNJOSLA ===== */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #030712 0%, #111827 100%) !important;
        padding: 20px 10px;
        border-right: 1px solid var(--card-border);
    }
    
    section[data-testid="stSidebar"] * {
        color: var(--text-primary) !important;
    }
    
    section[data-testid="stSidebar"] .stButton > button {
        background: rgba(255,255,255,0.05);
        box-shadow: none;
        border: 1px solid var(--card-border);
        margin-bottom: 5px;
        color: var(--text-primary) !important;
    }
    
    section[data-testid="stSidebar"] .stButton > button:hover {
        background: rgba(255,255,255,0.1);
    }
    
    /* ===== TABULAS ===== */
    .stDataFrame {
        border-radius: 16px !important;
        overflow: hidden;
        box-shadow: 0 4px 20px rgba(0,0,0,0.5);
        background: var(--card-bg) !important;
    }
    
    .stDataFrame table {
        width: 100%;
        border-collapse: collapse;
        background: var(--card-bg);
    }
    
    .stDataFrame th {
        background: linear-gradient(135deg, var(--gradient-start) 0%, var(--gradient-end) 100%);
        color: white !important;
        font-weight: 600;
        padding: 15px !important;
        text-align: left;
    }
    
    .stDataFrame td {
        padding: 12px 15px !important;
        border-bottom: 1px solid var(--card-border);
        color: var(--text-primary) !important;
        background: var(--card-bg) !important;
    }
    
    .stDataFrame tr:hover td {
        background: var(--lighter) !important;
    }
    
    /* ===== CILNES (TABS) ===== */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: var(--card-bg);
        padding: 10px;
        border-radius: 50px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.3);
        margin-bottom: 20px;
        border: 1px solid var(--card-border);
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 30px !important;
        padding: 12px 24px !important;
        font-weight: 600;
        transition: all 0.3s ease;
        color: var(--text-secondary) !important;
        background: transparent !important;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, var(--gradient-start) 0%, var(--gradient-end) 100%) !important;
        color: white !important;
    }
    
    /* ===== EXPANDER ===== */
    .streamlit-expanderHeader {
        background: var(--card-bg) !important;
        border-radius: 12px !important;
        padding: 15px !important;
        font-weight: 600 !important;
        color: var(--text-primary) !important;
        border: 1px solid var(--card-border) !important;
    }
    
    .streamlit-expanderContent {
        background: var(--card-bg) !important;
        border-radius: 0 0 12px 12px !important;
        padding: 15px !important;
        border: 1px solid var(--card-border);
        border-top: none;
        color: var(--text-primary) !important;
    }
    
    /* ===== LOGIN LAPA ===== */
    .login-container {
        display: flex;
        justify-content: center;
        align-items: center;
        min-height: 10vh;
        background: linear-gradient(135deg, #030712 0%, #111827 100%);
        padding: 10px;
        border-radius: 20px;
    }
    
    .login-card {
        background: var(--card-bg);
        border-radius: 20px;
        padding: 10px;
        box-shadow: 0 20px 60px rgba(0,0,0,0.7);
        width: 100%;
        max-width: 400px;
        animation: slideUp 0.5s ease;
        border: 1px solid var(--card-border);
    }
    
    @keyframes slideUp {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .login-card h1 {
        background: linear-gradient(135deg, var(--gradient-start) 0%, var(--gradient-end) 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2rem;
        font-weight: 700;
        text-align: center;
        margin-bottom: 5px;
    }
    
    .login-card .subtitle {
        color: var(--text-muted);
        text-align: center;
        margin-bottom: 5px;
    }
    
    /* ===== DALĪTĀJLĪNIJA ===== */
    .custom-divider {
        height: 2px;
        background: linear-gradient(90deg, transparent, var(--primary), transparent);
        margin: 30px 0;
    }
    
    hr {
        border: none;
        height: 1px;
        background: linear-gradient(90deg, transparent, var(--card-border), transparent);
        margin: 20px 0;
    }
    
    /* ===== PROGRESA BĀRS ===== */
    .stProgress > div > div {
        background: linear-gradient(135deg, var(--gradient-start) 0%, var(--gradient-end) 100%);
        border-radius: 10px;
    }
    
    /* ===== ALERTI / PAZIŅOJUMI ===== */
    .stAlert {
        border-radius: 16px;
        border: none;
        box-shadow: 0 4px 20px rgba(0,0,0,0.3);
        padding: 16px 20px;
        color: white !important;
    }
    
    .stAlert.success {
        background: linear-gradient(135deg, #065f46 0%, #047857 100%);
    }
    
    .stAlert.error {
        background: linear-gradient(135deg, #991b1b 0%, #b91c1c 100%);
    }
    
    .stAlert.warning {
        background: linear-gradient(135deg, #92400e 0%, #b45309 100%);
    }
    
    .stAlert.info {
        background: linear-gradient(135deg, #1e40af 0%, #1e3a8a 100%);
    }
    
    /* ===== LOADING SPINNER ===== */
    .stSpinner > div {
        border-color: var(--primary) transparent transparent transparent !important;
    }
    
    /* ===== RĒĶINU VĒSTURES SPECIFISKIE STILI ===== */
    .invoice-detail-card {
        background: var(--card-bg);
        border-radius: 16px;
        padding: 20px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.3);
        margin: 20px 0;
        border: 1px solid var(--card-border);
    }
    
    .invoice-detail-card h4 {
        color: var(--text-primary);
        margin-bottom: 15px;
        font-weight: 600;
        border-bottom: 2px solid var(--card-border);
        padding-bottom: 10px;
    }
    
    /* ===== CHECKBOXES UN RADIO ===== */
    .stCheckbox label,
    .stRadio label {
        color: var(--text-primary) !important;
    }
    
    /* ===== INFO TEKSTS ===== */
    .stInfo, .stWarning, .stError, .stSuccess {
        color: white !important;
    }
    
    /* ===== RESPONSĪVAIS DIZAINS ===== */
    @media (max-width: 768px) {
        .gradient-header {
            font-size: 1.8rem;
        }
        
        div[data-testid="metric-container"] {
            padding: 15px !important;
            margin-bottom: 10px;
        }
        
        div[data-testid="metric-container"] div {
            font-size: 24px !important;
        }
        
        .login-card {
            padding: 30px;
        }
        
        .stTabs [data-baseweb="tab"] {
            padding: 8px 16px !important;
            font-size: 14px;
        }
        
        .stDataFrame {
            font-size: 14px;
        }
        
        .stDataFrame th,
        .stDataFrame td {
            padding: 10px !important;
        }
    }
    
    @media (max-width: 480px) {
        .gradient-header {
            font-size: 1.5rem;
        }
        
        .login-card {
            padding: 25px;
        }
        
        .login-card h1 {
            font-size: 1.6rem;
        }
        
        .stButton > button {
            padding: 10px 16px;
            font-size: 14px;
        }
    }
    
    /* ===== PRINT STYLES ===== */
    @media print {
        section[data-testid="stSidebar"],
        .stButton,
        .stTabs {
            display: none !important;
        }
        
        .main {
            background: white;
            padding: 0;
        }
        
        body, p, div, h1, h2, h3 {
            color: black !important;
        }
    }
</style>
"""

COLORS = {
    'primary': '#818cf8',
    'primary_dark': '#6366f1',
    'secondary': '#34d399',
    'danger': '#f87171',
    'warning': '#fbbf24',
    'dark': '#111827',
    'darker': '#030712',
    'light': '#1f2937',
    'lighter': '#374151',
    'gray': '#9ca3af',
    'gray_light': '#6b7280',
    'gradient_start': '#4f46e5',
    'gradient_end': '#7c3aed',
    'text_primary': '#f9fafb',
    'text_secondary': '#e5e7eb',
    'text_muted': '#9ca3af'
}