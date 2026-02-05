"""
Firebase Authentication Integration
Provides email/password and Google OAuth authentication
"""
import streamlit as st
import json
import os
from typing import Optional, Dict, Any
import requests
from datetime import datetime, timedelta


class FirebaseAuth:
    """
    Firebase Authentication handler for Streamlit
    """
    
    def __init__(self, config: Optional[Dict[str, str]] = None):
        """
        Initialize Firebase Auth
        
        Args:
            config: Firebase configuration dictionary
        """
        if config is None:
            config = self._load_config()
        
        self.api_key = config.get('apiKey', os.getenv('FIREBASE_API_KEY', ''))
        self.auth_domain = config.get('authDomain', os.getenv('FIREBASE_AUTH_DOMAIN', ''))
        self.project_id = config.get('projectId', os.getenv('FIREBASE_PROJECT_ID', ''))
        
        # Firebase Auth REST API endpoints
        self.auth_url = f"https://identitytoolkit.googleapis.com/v1/accounts"
        
    def _load_config(self) -> Dict[str, str]:
        """Load Firebase config from file or environment"""
        config_path = os.path.join(os.path.dirname(__file__), '../config/firebase_config.json')
        
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                return json.load(f)
        
        # Return default/environment config
        return {
            'apiKey': os.getenv('FIREBASE_API_KEY', ''),
            'authDomain': os.getenv('FIREBASE_AUTH_DOMAIN', ''),
            'projectId': os.getenv('FIREBASE_PROJECT_ID', '')
        }
    
    def sign_in_with_email_password(self, email: str, password: str) -> Optional[Dict[str, Any]]:
        """
        Sign in with email and password
        
        Args:
            email: User email
            password: User password
            
        Returns:
            User data if successful, None otherwise
        """
        try:
            url = f"{self.auth_url}:signInWithPassword?key={self.api_key}"
            payload = {
                "email": email,
                "password": password,
                "returnSecureToken": True
            }
            
            response = requests.post(url, json=payload)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'user_id': data.get('localId'),
                    'email': data.get('email'),
                    'token': data.get('idToken'),
                    'refresh_token': data.get('refreshToken'),
                    'expires_in': data.get('expiresIn'),
                    'display_name': data.get('displayName', email.split('@')[0])
                }
            else:
                error_data = response.json()
                error_msg = error_data.get('error', {}).get('message', 'Authentication failed')
                # Sanitize error message - don't expose internal details
                if 'INVALID_PASSWORD' in error_msg:
                    st.error("Login failed: Invalid email or password")
                elif 'EMAIL_NOT_FOUND' in error_msg:
                    st.error("Login failed: Invalid email or password")
                elif 'USER_DISABLED' in error_msg:
                    st.error("Login failed: Account has been disabled")
                else:
                    st.error("Login failed: Please check your credentials and try again")
                return None
                
        except Exception as e:
            st.error(f"Authentication error: {str(e)}")
            return None
    
    def sign_up_with_email_password(self, email: str, password: str, display_name: str = "") -> Optional[Dict[str, Any]]:
        """
        Create new account with email and password
        
        Args:
            email: User email
            password: User password
            display_name: User's display name
            
        Returns:
            User data if successful, None otherwise
        """
        try:
            url = f"{self.auth_url}:signUp?key={self.api_key}"
            payload = {
                "email": email,
                "password": password,
                "returnSecureToken": True
            }
            
            response = requests.post(url, json=payload)
            
            if response.status_code == 200:
                data = response.json()
                
                # Update display name if provided
                if display_name:
                    self._update_profile(data.get('idToken'), display_name)
                
                return {
                    'user_id': data.get('localId'),
                    'email': data.get('email'),
                    'token': data.get('idToken'),
                    'refresh_token': data.get('refreshToken'),
                    'expires_in': data.get('expiresIn'),
                    'display_name': display_name or email.split('@')[0]
                }
            else:
                error_data = response.json()
                error_msg = error_data.get('error', {}).get('message', 'Signup failed')
                # Sanitize error messages
                if 'EMAIL_EXISTS' in error_msg:
                    st.error("Signup failed: Email already registered")
                elif 'WEAK_PASSWORD' in error_msg:
                    st.error("Signup failed: Password is too weak")
                elif 'INVALID_EMAIL' in error_msg:
                    st.error("Signup failed: Invalid email format")
                else:
                    st.error("Signup failed: Please check your information and try again")
                return None
                
        except Exception as e:
            st.error(f"Signup error: {str(e)}")
            return None
    
    def _update_profile(self, id_token: str, display_name: str) -> bool:
        """Update user profile"""
        try:
            url = f"{self.auth_url}:update?key={self.api_key}"
            payload = {
                "idToken": id_token,
                "displayName": display_name,
                "returnSecureToken": True
            }
            
            response = requests.post(url, json=payload)
            return response.status_code == 200
        except:
            return False
    
    def refresh_token(self, refresh_token: str) -> Optional[Dict[str, Any]]:
        """
        Refresh the authentication token
        
        Args:
            refresh_token: Refresh token from previous authentication
            
        Returns:
            New token data if successful
        """
        try:
            url = f"https://securetoken.googleapis.com/v1/token?key={self.api_key}"
            payload = {
                "grant_type": "refresh_token",
                "refresh_token": refresh_token
            }
            
            response = requests.post(url, json=payload)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'token': data.get('id_token'),
                    'refresh_token': data.get('refresh_token'),
                    'expires_in': data.get('expires_in')
                }
            return None
        except:
            return None
    
    def verify_token(self, id_token: str) -> Optional[Dict[str, Any]]:
        """
        Verify an ID token
        
        Args:
            id_token: Firebase ID token
            
        Returns:
            User data if token is valid
        """
        try:
            url = f"{self.auth_url}:lookup?key={self.api_key}"
            payload = {"idToken": id_token}
            
            response = requests.post(url, json=payload)
            
            if response.status_code == 200:
                data = response.json()
                users = data.get('users', [])
                if users:
                    user = users[0]
                    return {
                        'user_id': user.get('localId'),
                        'email': user.get('email'),
                        'display_name': user.get('displayName', user.get('email', '').split('@')[0]),
                        'email_verified': user.get('emailVerified', False)
                    }
            return None
        except:
            return None


class SessionManager:
    """
    Manage user sessions in Streamlit
    """
    
    @staticmethod
    def init_session():
        """Initialize session state variables"""
        if 'authenticated' not in st.session_state:
            st.session_state.authenticated = False
        if 'user' not in st.session_state:
            st.session_state.user = None
        if 'token' not in st.session_state:
            st.session_state.token = None
        if 'login_time' not in st.session_state:
            st.session_state.login_time = None
    
    @staticmethod
    def login(user_data: Dict[str, Any]):
        """Set user as logged in"""
        st.session_state.authenticated = True
        st.session_state.user = {
            'user_id': user_data.get('user_id'),
            'email': user_data.get('email'),
            'display_name': user_data.get('display_name'),
            'role': user_data.get('role', 'user')  # Default role
        }
        st.session_state.token = user_data.get('token')
        st.session_state.refresh_token = user_data.get('refresh_token')
        st.session_state.login_time = datetime.now()
    
    @staticmethod
    def logout():
        """Log out the user"""
        st.session_state.authenticated = False
        st.session_state.user = None
        st.session_state.token = None
        st.session_state.refresh_token = None
        st.session_state.login_time = None
    
    @staticmethod
    def is_authenticated() -> bool:
        """Check if user is authenticated"""
        return st.session_state.get('authenticated', False)
    
    @staticmethod
    def get_user() -> Optional[Dict[str, Any]]:
        """Get current user data"""
        return st.session_state.get('user')
    
    @staticmethod
    def check_session_expiry() -> bool:
        """
        Check if session has expired (1 hour timeout)
        
        Returns:
            True if session is still valid, False if expired
        """
        if not SessionManager.is_authenticated():
            return False
        
        login_time = st.session_state.get('login_time')
        if not login_time:
            return False
        
        # Check if more than 1 hour has passed
        if datetime.now() - login_time > timedelta(hours=1):
            SessionManager.logout()
            return False
        
        return True


def require_auth(func):
    """
    Decorator to require authentication for a function/page
    
    Usage:
        @require_auth
        def my_protected_page():
            st.write("This page requires authentication")
    """
    def wrapper(*args, **kwargs):
        SessionManager.init_session()
        
        if not SessionManager.check_session_expiry():
            st.warning("⚠️ Please log in to access this page")
            st.stop()
        
        return func(*args, **kwargs)
    
    return wrapper
