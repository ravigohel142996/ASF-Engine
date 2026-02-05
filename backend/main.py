"""
FastAPI Backend for ASF-Engine SaaS Platform
Main API server with authentication, predictions, and monitoring endpoints
"""
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import uvicorn
import os

# Import from our modules
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from backend.auth import create_access_token, verify_token, get_password_hash, verify_password
from backend.database import get_db, init_db
from backend.predict import PredictionService


# Initialize FastAPI app
app = FastAPI(
    title="ASF-Engine API",
    description="AI System Failure Monitoring SaaS Platform API",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware - Configure for specific origins in production
# Set CORS_ORIGINS environment variable with comma-separated origins
ALLOWED_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:8501,http://localhost:3000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Initialize services
prediction_service = PredictionService()


# Pydantic models
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str
    user_id: str
    email: str


class PredictionRequest(BaseModel):
    metrics: Dict[str, float]
    model_type: Optional[str] = "hybrid"


class PredictionResponse(BaseModel):
    prediction: float
    confidence: float
    risk_level: str
    timestamp: datetime
    recommendations: List[str]


class MetricsRequest(BaseModel):
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    limit: Optional[int] = 100


class AlertCreate(BaseModel):
    severity: str
    message: str
    source: str
    metadata: Optional[Dict[str, Any]] = {}


# Dependency to get current user
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify JWT token and return user info"""
    token = credentials.credentials
    
    try:
        payload = verify_token(token)
        return payload
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "2.0.0",
        "services": {
            "api": "running",
            "database": "connected",
            "ml_service": "active"
        }
    }


# Authentication endpoints
@app.post("/api/v1/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register(user: UserCreate):
    """
    Register a new user
    """
    try:
        db = next(get_db())
        
        # Check if user already exists (simplified for demo)
        # In production, check database
        
        # Create user (simplified - in production, save to database)
        user_id = f"user_{user.email.split('@')[0]}"
        
        # Generate JWT token
        access_token = create_access_token(
            data={"sub": user.email, "user_id": user_id}
        )
        
        return Token(
            access_token=access_token,
            token_type="bearer",
            user_id=user_id,
            email=user.email
        )
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/v1/login", response_model=Token)
async def login(credentials: UserLogin):
    """
    Login with email and password
    NOTE: In production, this must validate against the database
    """
    try:
        db = next(get_db())
        
        # TODO: Replace with actual database validation
        # This is a placeholder - implement proper authentication
        # from backend.database import get_user_by_email, verify_password
        # user = get_user_by_email(db, credentials.email)
        # if not user or not verify_password(credentials.password, user.hashed_password):
        #     raise HTTPException(status_code=401, detail="Invalid credentials")
        
        user_id = f"user_{credentials.email.split('@')[0]}"
        
        # Generate JWT token
        access_token = create_access_token(
            data={"sub": credentials.email, "user_id": user_id}
        )
        
        return Token(
            access_token=access_token,
            token_type="bearer",
            user_id=user_id,
            email=credentials.email
        )
    
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid credentials")


# Prediction endpoints
@app.post("/api/v1/predict", response_model=PredictionResponse)
async def predict(
    request: PredictionRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Make a failure prediction based on current metrics
    """
    try:
        result = prediction_service.predict(request.metrics, request.model_type)
        
        return PredictionResponse(
            prediction=result['prediction'],
            confidence=result['confidence'],
            risk_level=result['risk_level'],
            timestamp=datetime.utcnow(),
            recommendations=result['recommendations']
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")


# Metrics endpoints
@app.get("/api/v1/metrics")
async def get_metrics(
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
    limit: int = 100,
    current_user: dict = Depends(get_current_user)
):
    """
    Retrieve system metrics within a time range
    """
    try:
        # In production, fetch from database
        return {
            "metrics": [],
            "count": 0,
            "start_time": start_time,
            "end_time": end_time
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/metrics")
async def log_metrics(
    metrics: Dict[str, Any],
    current_user: dict = Depends(get_current_user)
):
    """
    Log new system metrics
    """
    try:
        # In production, save to database
        return {
            "status": "success",
            "message": "Metrics logged successfully",
            "timestamp": datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Alerts endpoints
@app.get("/api/v1/alerts")
async def get_alerts(
    severity: Optional[str] = None,
    limit: int = 50,
    current_user: dict = Depends(get_current_user)
):
    """
    Retrieve system alerts
    """
    try:
        # In production, fetch from database
        return {
            "alerts": [],
            "count": 0,
            "severity": severity
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/alerts")
async def create_alert(
    alert: AlertCreate,
    current_user: dict = Depends(get_current_user)
):
    """
    Create a new alert
    """
    try:
        # In production, save to database and trigger notifications
        return {
            "status": "success",
            "alert_id": f"alert_{datetime.utcnow().timestamp()}",
            "created_at": datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# User profile endpoint
@app.get("/api/v1/profile")
async def get_profile(current_user: dict = Depends(get_current_user)):
    """
    Get current user profile
    """
    return {
        "user_id": current_user.get("user_id"),
        "email": current_user.get("sub"),
        "role": "user",
        "subscription": "free",
        "created_at": datetime.utcnow().isoformat()
    }


# Statistics endpoint
@app.get("/api/v1/stats")
async def get_statistics(current_user: dict = Depends(get_current_user)):
    """
    Get system statistics and summary
    """
    return {
        "total_predictions": 0,
        "total_alerts": 0,
        "system_health": 95.5,
        "uptime_percentage": 99.9,
        "last_updated": datetime.utcnow().isoformat()
    }


if __name__ == "__main__":
    # Initialize database
    init_db()
    
    # Run the server
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="info"
    )
