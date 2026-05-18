# components.py
import streamlit as st

def sidebar_header(user):
    """Render sidebar header with user info"""
    st.markdown("""
    <div class="sidebar-header" style="text-align: center; padding: 20px 0;">
        <div style="font-size: 60px; margin-bottom: 10px;">🏗️</div>
        <h2 style="color: white; margin: 0;">Projekta</h2>
        <p style="color: #9ca3af; margin: 0;">Management System</p>
    </div>
    <hr style="border-color: #374151;">
    """, unsafe_allow_html=True)
    
    if user and len(user) > 1:
        st.markdown(f"""
        <div class="sidebar-header" style="padding: 10px 0; color: white;">
            <div style="display: flex; align-items: center;">
                <div style="background: #6366f1; border-radius: 50%; width: 40px; height: 40px; 
                            display: flex; align-items: center; justify-content: center; margin-right: 10px;">
                    {user[1][0].upper() if user[1] else 'U'}
                </div>
                <div>
                    <div style="font-weight: 600;">{user[1]}</div>
                    <div style="font-size: 12px; color: #9ca3af;">{user[3].title()}</div>
                </div>
            </div>
        </div>
        <hr style="border-color: #374151;">
        """, unsafe_allow_html=True)

def navigation_menu(role):
    """Create navigation menu based on user role"""
    if role == "admin":
        return {
            "Dashboard": "📊",
            "Lietotāji": "👥",
            "Projekti": "🏗️",
            "Piesaistes": "🔗"
        }
    elif role == "manager":
        return {
            "Dashboard": "📊",
            "Rēķini": "📄"
        }
    else:  # worker
        return {
            "Dashboard": "📊",
            "Materiāli": "📦",
            "Stundas": "⏱️",
            "Transports": "🚗"
        }