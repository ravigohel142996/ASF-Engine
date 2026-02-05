"""
Database configuration and models using SQLAlchemy
"""
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

# Database URL
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable must be set")

# Validate PostgreSQL URL for production
if "sqlite" in DATABASE_URL.lower():
    import warnings
    warnings.warn(
        "Using SQLite database. This is only suitable for development. "
        "Use PostgreSQL for production deployments.",
        RuntimeWarning
    )

# Create engine
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

# Session maker
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


# Database Models
class User(Base):
    """User model with enhanced authentication fields"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    role = Column(String, default="user")  # user, admin, manager
    subscription_plan = Column(String, default="free")
    
    # Authentication fields
    email_verified = Column(Boolean, default=False)
    email_verification_token = Column(String, nullable=True)
    password_reset_token = Column(String, nullable=True)
    password_reset_expires = Column(DateTime, nullable=True)
    
    # Firebase integration
    firebase_uid = Column(String, unique=True, nullable=True, index=True)
    
    # Security tracking
    last_login = Column(DateTime, nullable=True)
    login_attempts = Column(Integer, default=0)
    locked_until = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Metric(Base):
    """System metrics model"""
    __tablename__ = "metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    metric_type = Column(String, index=True)
    value = Column(Float)
    unit = Column(String)
    metadata = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)


class Alert(Base):
    """Alert model"""
    __tablename__ = "alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    severity = Column(String, index=True)  # critical, warning, info
    status = Column(String, default="open")  # open, acknowledged, resolved
    message = Column(Text)
    source = Column(String)
    metadata = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    resolved_at = Column(DateTime, nullable=True)


class Log(Base):
    """System log model"""
    __tablename__ = "logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    level = Column(String, index=True)  # debug, info, warning, error, critical
    message = Column(Text)
    source = Column(String)
    metadata = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)


class Model(Base):
    """ML Model metadata"""
    __tablename__ = "models"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    version = Column(String)
    model_type = Column(String)  # lstm, xgboost, hybrid
    accuracy = Column(Float)
    is_active = Column(Boolean, default=False)
    metadata = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Session(Base):
    """User session model"""
    __tablename__ = "sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    token = Column(String, unique=True, index=True)
    ip_address = Column(String)
    user_agent = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)
    last_activity = Column(DateTime, default=datetime.utcnow)


# Database initialization
def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)


# Dependency to get database session
def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# CRUD operations helper (simplified examples)
def create_user(db, email: str, hashed_password: str, full_name: str, firebase_uid: str = None):
    """Create a new user"""
    user = User(
        email=email,
        hashed_password=hashed_password,
        full_name=full_name,
        firebase_uid=firebase_uid
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_user_by_email(db, email: str):
    """Get user by email"""
    return db.query(User).filter(User.email == email).first()


def get_user_by_firebase_uid(db, firebase_uid: str):
    """Get user by Firebase UID"""
    return db.query(User).filter(User.firebase_uid == firebase_uid).first()


def update_user_last_login(db, user_id: int):
    """Update user's last login timestamp"""
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        user.last_login = datetime.utcnow()
        user.login_attempts = 0
        db.commit()
    return user


def increment_login_attempts(db, email: str):
    """Increment failed login attempts"""
    user = db.query(User).filter(User.email == email).first()
    if user:
        user.login_attempts += 1
        # Lock account after 5 failed attempts for 30 minutes
        if user.login_attempts >= 5:
            user.locked_until = datetime.utcnow() + timedelta(minutes=30)
        db.commit()
    return user


def set_password_reset_token(db, email: str, token: str):
    """Set password reset token"""
    user = db.query(User).filter(User.email == email).first()
    if user:
        user.password_reset_token = token
        user.password_reset_expires = datetime.utcnow() + timedelta(hours=1)
        db.commit()
    return user


def verify_password_reset_token(db, token: str):
    """Verify and get user by password reset token"""
    user = db.query(User).filter(
        User.password_reset_token == token,
        User.password_reset_expires > datetime.utcnow()
    ).first()
    return user


def set_email_verification_token(db, user_id: int, token: str):
    """Set email verification token"""
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        user.email_verification_token = token
        db.commit()
    return user


def verify_email(db, token: str):
    """Verify email with token"""
    user = db.query(User).filter(User.email_verification_token == token).first()
    if user:
        user.email_verified = True
        user.email_verification_token = None
        db.commit()
    return user


def update_user_password(db, user_id: int, hashed_password: str):
    """Update user password"""
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        user.hashed_password = hashed_password
        user.password_reset_token = None
        user.password_reset_expires = None
        db.commit()
    return user


def create_metric(db, user_id: int, metric_type: str, value: float, unit: str = "", metadata: dict = None):
    """Create a new metric record"""
    metric = Metric(
        user_id=user_id,
        metric_type=metric_type,
        value=value,
        unit=unit,
        metadata=metadata or {}
    )
    db.add(metric)
    db.commit()
    db.refresh(metric)
    return metric


def create_alert(db, user_id: int, severity: str, message: str, source: str, metadata: dict = None):
    """Create a new alert"""
    alert = Alert(
        user_id=user_id,
        severity=severity,
        message=message,
        source=source,
        metadata=metadata or {}
    )
    db.add(alert)
    db.commit()
    db.refresh(alert)
    return alert
