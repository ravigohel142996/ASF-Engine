"""
Firebase Authentication Integration
Provides email/password and Google OAuth authentication
Integrated with PostgreSQL database for user management
"""
import streamlit as st
import json
import os
import sys
from typing import Optional, Dict, Any
import requests
from datetime import datetime, timedelta

# Add backend to path for database access
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from backend.database import (
    SessionLocal, get_user_by_email, get_user_by_firebase_uid,
    create_user, update_user_last_login, increment_login_attempts,
    set_email_verification_token, verify_email
)
from backend.auth import get_password_hash, verify_password
from auth.email_service import EmailService, generate_verification_token


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
        
        # Check if Firebase is configured
        self.is_firebase_configured = bool(self.api_key and self.project_id)
        
        # Initialize email service
        self.email_service = EmailService()
        
        # Demo credentials for testing when Firebase is not configured
        self.demo_email = os.getenv('DEMO_EMAIL', 'admin@test.com')
        self.demo_password = os.getenv('DEMO_PASSWORD', '1234')
        
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
        Supports both Firebase and PostgreSQL authentication
        
        Args:
            email: User email
            password: User password
            
        Returns:
            User data if successful, None otherwise
        """
        try:
            # Get database session
            db = SessionLocal()
            
            try:
                # First check if user exists in PostgreSQL
                db_user = get_user_by_email(db, email)
                
                # Check for account lockout
                if db_user and db_user.locked_until:
                    if db_user.locked_until > datetime.utcnow():
                        st.error(f"Account locked due to too many failed attempts. Try again later.")
                        return None
                    else:
                        # Unlock account if lockout period has passed
                        db_user.locked_until = None
                        db_user.login_attempts = 0
                        db.commit()
                
                # Try Firebase authentication if configured
                if self.is_firebase_configured:
                    url = f"{self.auth_url}:signInWithPassword?key={self.api_key}"
                    payload = {
                        "email": email,
                        "password": password,
                        "returnSecureToken": True
                    }
                    
                    response = requests.post(url, json=payload)
                    
                    if response.status_code == 200:
                        data = response.json()
                        firebase_uid = data.get('localId')
                        
                        # Update or create user in PostgreSQL
                        if not db_user:
                            db_user = create_user(
                                db, email, 
                                get_password_hash(password),
                                data.get('displayName', email.split('@')[0]),
                                firebase_uid
                            )
                        
                        # Update last login
                        update_user_last_login(db, db_user.id)
                        
                        return {
                            'user_id': str(db_user.id),
                            'email': db_user.email,
                            'token': data.get('idToken'),
                            'refresh_token': data.get('refreshToken'),
                            'expires_in': data.get('expiresIn'),
                            'display_name': db_user.full_name or email.split('@')[0],
                            'role': db_user.role,
                            'email_verified': db_user.email_verified
                        }
                    else:
                        # Firebase auth failed
                        if db_user:
                            increment_login_attempts(db, email)
                        error_data = response.json()
                        error_msg = error_data.get('error', {}).get('message', 'Authentication failed')
                        if 'INVALID_PASSWORD' in error_msg or 'EMAIL_NOT_FOUND' in error_msg:
                            st.error("❌ Invalid email or password")
                        elif 'USER_DISABLED' in error_msg:
                            st.error("❌ Account has been disabled")
                        else:
                            st.error("❌ Authentication failed. Please try again.")
                        return None
                
                # Fallback to PostgreSQL authentication
                elif db_user:
                    if verify_password(password, db_user.hashed_password):
                        # Successful login
                        update_user_last_login(db, db_user.id)
                        
                        return {
                            'user_id': str(db_user.id),
                            'email': db_user.email,
                            'token': None,  # JWT will be generated separately
                            'refresh_token': None,
                            'expires_in': 3600,
                            'display_name': db_user.full_name or email.split('@')[0],
                            'role': db_user.role,
                            'email_verified': db_user.email_verified
                        }
                    else:
                        # Wrong password
                        increment_login_attempts(db, email)
                        st.error("❌ Invalid email or password")
                        return None
                
                # Demo mode fallback
                elif email == self.demo_email and password == self.demo_password:
                    st.info("🔓 Demo mode: Creating temporary account")
                    db_user = create_user(
                        db, email,
                        get_password_hash(password),
                        "Demo User"
                    )
                    db_user.email_verified = True
                    db.commit()
                    
                    return {
                        'user_id': str(db_user.id),
                        'email': db_user.email,
                        'token': None,
                        'refresh_token': None,
                        'expires_in': 3600,
                        'display_name': db_user.full_name,
                        'role': db_user.role,
                        'email_verified': True
                    }
                else:
                    st.error("❌ Invalid email or password")
                    return None
                    
            finally:
                db.close()
                
        except Exception as e:
            st.error(f"❌ Authentication error: {str(e)}")
            return None
    
    def sign_up_with_email_password(self, email: str, password: str, display_name: str = "") -> Optional[Dict[str, Any]]:
        """
        Create new account with email and password
        Supports both Firebase and PostgreSQL user creation
        
        Args:
            email: User email
            password: User password
            display_name: User's display name
            
        Returns:
            User data if successful, None otherwise
        """
        try:
            # Get database session
            db = SessionLocal()
            
            try:
                # Check if user already exists
                existing_user = get_user_by_email(db, email)
                if existing_user:
                    st.error("❌ Email already registered. Please login instead.")
                    return None
                
                # Validate password strength
                if len(password) < 6:
                    st.error("❌ Password must be at least 6 characters")
                    return None
                
                firebase_uid = None
                id_token = None
                refresh_token = None
                
                # Try Firebase signup if configured
                if self.is_firebase_configured:
                    url = f"{self.auth_url}:signUp?key={self.api_key}"
                    payload = {
                        "email": email,
                        "password": password,
                        "returnSecureToken": True
                    }
                    
                    response = requests.post(url, json=payload)
                    
                    if response.status_code == 200:
                        data = response.json()
                        firebase_uid = data.get('localId')
                        id_token = data.get('idToken')
                        refresh_token = data.get('refreshToken')
                        
                        # Update display name in Firebase
                        if display_name:
                            self._update_profile(id_token, display_name)
                    else:
                        error_data = response.json()
                        error_msg = error_data.get('error', {}).get('message', 'Signup failed')
                        if 'EMAIL_EXISTS' in error_msg:
                            st.error("❌ Email already registered")
                        elif 'WEAK_PASSWORD' in error_msg:
                            st.error("❌ Password is too weak")
                        elif 'INVALID_EMAIL' in error_msg:
                            st.error("❌ Invalid email format")
                        else:
                            st.error("❌ Signup failed. Please try again.")
                        return None
                
                # Create user in PostgreSQL
                hashed_password = get_password_hash(password)
                db_user = create_user(
                    db, email, hashed_password,
                    display_name or email.split('@')[0],
                    firebase_uid
                )
                
                # Generate email verification token
                verification_token = generate_verification_token()
                set_email_verification_token(db, db_user.id, verification_token)
                
                # Send verification email
                self.email_service.send_verification_email(
                    email, verification_token, display_name
                )
                
                return {
                    'user_id': str(db_user.id),
                    'email': db_user.email,
                    'token': id_token,
                    'refresh_token': refresh_token,
                    'expires_in': 3600,
                    'display_name': db_user.full_name,
                    'role': db_user.role,
                    'email_verified': False
                }
                
            finally:
                db.close()
                
        except Exception as e:
            st.error(f"❌ Signup error: {str(e)}")
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
    
    def request_password_reset(self, email: str) -> bool:
        """
        Request password reset via email
        
        Args:
            email: User's email address
            
        Returns:
            True if reset email sent successfully
        """
        try:
            db = SessionLocal()
            
            try:
                # Check if user exists
                db_user = get_user_by_email(db, email)
                
                if not db_user:
                    # Don't reveal if email exists
                    st.success("✅ If your email is registered, you will receive a password reset link.")
                    return True
                
                # Generate reset token
                from backend.database import set_password_reset_token
                from auth.email_service import generate_password_reset_token
                
                reset_token = generate_password_reset_token()
                set_password_reset_token(db, email, reset_token)
                
                # Send reset email
                self.email_service.send_password_reset_email(
                    email, reset_token, db_user.full_name
                )
                
                st.success("✅ If your email is registered, you will receive a password reset link.")
                return True
                
            finally:
                db.close()
                
        except Exception as e:
            st.error(f"❌ Error processing password reset: {str(e)}")
            return False
    
    def reset_password_with_token(self, token: str, new_password: str) -> bool:
        """
        Reset password using token
        
        Args:
            token: Password reset token
            new_password: New password
            
        Returns:
            True if password reset successfully
        """
        try:
            if len(new_password) < 6:
                st.error("❌ Password must be at least 6 characters")
                return False
            
            db = SessionLocal()
            
            try:
                from backend.database import verify_password_reset_token, update_user_password
                
                # Verify token and get user
                db_user = verify_password_reset_token(db, token)
                
                if not db_user:
                    st.error("❌ Invalid or expired reset token")
                    return False
                
                # Hash new password
                hashed_password = get_password_hash(new_password)
                
                # Update password
                update_user_password(db, db_user.id, hashed_password)
                
                st.success("✅ Password reset successfully! You can now login with your new password.")
                return True
                
            finally:
                db.close()
                
        except Exception as e:
            st.error(f"❌ Error resetting password: {str(e)}")
            return False
    
    def verify_email_with_token(self, token: str) -> bool:
        """
        Verify email address using token
        
        Args:
            token: Email verification token
            
        Returns:
            True if email verified successfully
        """
        try:
            db = SessionLocal()
            
            try:
                # Verify email
                db_user = verify_email(db, token)
                
                if not db_user:
                    st.error("❌ Invalid or expired verification token")
                    return False
                
                # Send welcome email
                self.email_service.send_welcome_email(
                    db_user.email, db_user.full_name
                )
                
                st.success(f"✅ Email verified successfully! Welcome, {db_user.full_name}!")
                return True
                
            finally:
                db.close()
                
        except Exception as e:
            st.error(f"❌ Error verifying email: {str(e)}")
            return False


class SessionManager:
    """
    Manage user sessions in Streamlit with database backing
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
            'role': user_data.get('role', 'user'),
            'email_verified': user_data.get('email_verified', False)
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
    
    @staticmethod
    def has_role(role: str) -> bool:
        """
        Check if user has specific role
        
        Args:
            role: Role to check (e.g., 'admin', 'manager', 'user')
            
        Returns:
            True if user has the role
        """
        user = SessionManager.get_user()
        if not user:
            return False
        return user.get('role', 'user') == role
    
    @staticmethod
    def is_admin() -> bool:
        """Check if current user is admin"""
        return SessionManager.has_role('admin')
    
    @staticmethod
    def is_email_verified() -> bool:
        """Check if user's email is verified"""
        user = SessionManager.get_user()
        if not user:
            return False
        return user.get('email_verified', False)
    
    @staticmethod
    def require_email_verification() -> bool:
        """
        Check email verification and show warning if not verified
        
        Returns:
            True if verified, False otherwise
        """
        if not SessionManager.is_email_verified():
            st.warning("⚠️ Please verify your email address to access all features.")
            st.info("📧 Check your inbox for the verification email. Didn't receive it? Contact support.")
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


def require_role(role: str):
    """
    Decorator to require specific role for a function/page
    
    Args:
        role: Required role (e.g., 'admin', 'manager')
    
    Usage:
        @require_role('admin')
        def admin_page():
            st.write("This page is for admins only")
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            SessionManager.init_session()
            
            if not SessionManager.check_session_expiry():
                st.warning("⚠️ Please log in to access this page")
                st.stop()
            
            if not SessionManager.has_role(role):
                st.error(f"❌ Access denied. This page requires '{role}' role.")
                st.stop()
            
            return func(*args, **kwargs)
        return wrapper
    return decorator
