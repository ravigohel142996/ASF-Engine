"""
Simple Local Authentication for ASF-Engine
No Firebase, No Database, No Environment Variables
Uses Streamlit session_state for session management
"""
import streamlit as st
from datetime import datetime, timedelta
from typing import Optional, Dict, Any


# Hardcoded credentials
ADMIN_EMAIL = "admin@asf.com"
ADMIN_PASSWORD = "123456"


class SimpleAuth:
    """
    Simple authentication handler using hardcoded credentials
    """
    
    @staticmethod
    def login(email: str, password: str) -> bool:
        """
        Authenticate user with hardcoded credentials
        
        Args:
            email: User email
            password: User password
            
        Returns:
            True if authentication successful, False otherwise
        """
        if email == ADMIN_EMAIL and password == ADMIN_PASSWORD:
            # Set session state
            st.session_state.authenticated = True
            st.session_state.user = {
                'user_id': '1',
                'email': ADMIN_EMAIL,
                'display_name': 'Admin User',
                'role': 'admin',
                'email_verified': True
            }
            st.session_state.login_time = datetime.now()
            return True
        return False
    
    @staticmethod
    def logout():
        """Log out the current user"""
        st.session_state.authenticated = False
        st.session_state.user = None
        st.session_state.login_time = None
    
    @staticmethod
    def is_logged_in() -> bool:
        """
        Check if user is logged in and session is valid
        
        Returns:
            True if user is authenticated and session is valid
        """
        # Initialize session state if not exists
        if 'authenticated' not in st.session_state:
            st.session_state.authenticated = False
        if 'user' not in st.session_state:
            st.session_state.user = None
        if 'login_time' not in st.session_state:
            st.session_state.login_time = None
        
        # Check authentication
        if not st.session_state.get('authenticated', False):
            return False
        
        # Check session expiry (1 hour timeout)
        login_time = st.session_state.get('login_time')
        if login_time and datetime.now() - login_time > timedelta(hours=1):
            SimpleAuth.logout()
            return False
        
        return True
    
    @staticmethod
    def get_user() -> Optional[Dict[str, Any]]:
        """
        Get current user data
        
        Returns:
            User dictionary if logged in, None otherwise
        """
        if SimpleAuth.is_logged_in():
            return st.session_state.get('user')
        return None
    
    @staticmethod
    def init_session():
        """Initialize session state variables"""
        if 'authenticated' not in st.session_state:
            st.session_state.authenticated = False
        if 'user' not in st.session_state:
            st.session_state.user = None
        if 'login_time' not in st.session_state:
            st.session_state.login_time = None
