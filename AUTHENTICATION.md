# Authentication System Documentation

## Overview

ASF-Engine implements a production-ready authentication system with multiple layers of security:

- **Firebase Authentication** (optional): Enterprise-grade auth provider
- **JWT Tokens**: Secure API authentication
- **PostgreSQL Database**: User data persistence
- **Email Verification**: Account verification via email
- **Password Reset**: Secure password recovery
- **Role-Based Access Control**: Fine-grained permissions
- **Session Management**: Secure session handling

## Quick Start

### 1. Environment Setup

Create a `.env` file from `.env.example`:

```bash
cp .env.example .env
```

Configure the following required variables:

```env
# Required: Database
DATABASE_URL=postgresql://user:password@localhost:5432/asf_engine

# Required: JWT Secret (must be 32+ characters)
JWT_SECRET_KEY=your-very-long-secret-key-at-least-32-characters

# Optional: Firebase (for Firebase Auth)
FIREBASE_API_KEY=your_api_key
FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
FIREBASE_PROJECT_ID=your-project-id

# Optional: Email (for verification & password reset)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password
BASE_URL=http://localhost:8501

# Demo Mode Credentials
DEMO_EMAIL=admin@test.com
DEMO_PASSWORD=1234
```

### 2. Database Initialization

Initialize the database and create tables:

```bash
python scripts/init_db.py
```

This will:
- Create all necessary database tables
- Create a default admin user (using DEMO_EMAIL/DEMO_PASSWORD)

### 3. Start the Application

```bash
# Start Streamlit frontend
streamlit run app.py

# Start FastAPI backend (in another terminal)
python backend/main.py
```

## Authentication Modes

### Mode 1: Firebase + PostgreSQL (Recommended for Production)

**Setup:**
1. Create a Firebase project at https://console.firebase.google.com/
2. Enable Email/Password authentication
3. Get your Firebase credentials (API Key, Project ID, Auth Domain)
4. Configure in `.env` file
5. Install pyrebase4: `pip install pyrebase4`

**Features:**
- Enterprise-grade authentication using Pyrebase4
- Social login support (Google, Facebook, etc.)
- Automatic token refresh
- Built-in security rules
- User data synced to PostgreSQL
- Graceful fallback to REST API if pyrebase not available

**Implementation:**
The system uses Pyrebase4 for Firebase authentication, which provides:
- Better error handling
- Built-in token management
- Simpler API for authentication operations
- Automatic request retry logic

If pyrebase4 is not installed, the system automatically falls back to Firebase REST API.

### Mode 2: PostgreSQL Only (Self-Hosted)

**Setup:**
1. Configure only `DATABASE_URL` and `JWT_SECRET_KEY`
2. Leave Firebase variables empty

**Features:**
- Full control over authentication
- No external dependencies
- Custom authentication logic
- Email/password login
- JWT token-based sessions

### Mode 3: Demo Mode (Development)

**Setup:**
1. Use default DEMO_EMAIL and DEMO_PASSWORD
2. No Firebase or SMTP required

**Features:**
- Quick testing without setup
- Default credentials: `admin@test.com` / `1234`
- Auto-creates user on first login
- Email verification bypassed

## User Roles

The system supports role-based access control:

| Role | Description | Permissions |
|------|-------------|-------------|
| `user` | Regular user | View dashboard, manage own data |
| `manager` | Manager | All user permissions + team management |
| `admin` | Administrator | Full system access |

### Using Roles in Code

```python
from auth.firebase_auth import SessionManager, require_role

# Check if user is admin
if SessionManager.is_admin():
    st.write("Admin controls")

# Require specific role for page
@require_role('admin')
def admin_page():
    st.write("Admin only page")
```

## Email Features

### Email Verification

When a user signs up:
1. Account is created but `email_verified = False`
2. Verification email sent with unique token
3. User clicks link in email → redirects to `/verify-email?token=...`
4. Email verified, welcome email sent

**Check verification status:**
```python
if SessionManager.is_email_verified():
    st.write("Verified user")
else:
    st.warning("Please verify your email")
```

### Password Reset

Password reset flow:
1. User clicks "Forgot Password" on login page
2. Enters email address
3. Reset email sent with unique token (expires in 1 hour)
4. User clicks link → redirects to `/reset-password?token=...`
5. User enters new password
6. Password updated, token invalidated

## Security Features

### Account Lockout

After 5 failed login attempts:
- Account locked for 30 minutes
- User sees error message
- Lockout automatically expires

### Session Management

- Sessions expire after 1 hour of inactivity
- Automatic logout on expiry
- Session data encrypted and stored securely

### Password Requirements

- Minimum 6 characters (customizable)
- Hashed using bcrypt
- Never stored in plain text

### Token Security

- JWT tokens with expiration
- Password reset tokens expire in 1 hour
- Email verification tokens expire in 24 hours
- Tokens are single-use and invalidated after use

## API Endpoints (FastAPI Backend)

### Authentication Endpoints

```
POST /api/v1/register
Body: { "email": "user@example.com", "password": "pass123", "full_name": "John Doe" }
Response: { "access_token": "...", "token_type": "bearer", ... }

POST /api/v1/login
Body: { "email": "user@example.com", "password": "pass123" }
Response: { "access_token": "...", "token_type": "bearer", ... }

GET /api/v1/profile
Headers: { "Authorization": "Bearer <token>" }
Response: { "user_id": "...", "email": "...", "role": "user" }
```

### Using JWT Tokens

```python
import requests

# Login
response = requests.post(
    "http://localhost:8000/api/v1/login",
    json={"email": "admin@test.com", "password": "1234"}
)
token = response.json()["access_token"]

# Make authenticated request
headers = {"Authorization": f"Bearer {token}"}
profile = requests.get(
    "http://localhost:8000/api/v1/profile",
    headers=headers
)
```

## Database Schema

### Users Table

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR UNIQUE NOT NULL,
    hashed_password VARCHAR NOT NULL,
    full_name VARCHAR,
    is_active BOOLEAN DEFAULT TRUE,
    is_admin BOOLEAN DEFAULT FALSE,
    role VARCHAR DEFAULT 'user',
    subscription_plan VARCHAR DEFAULT 'free',
    
    -- Authentication fields
    email_verified BOOLEAN DEFAULT FALSE,
    email_verification_token VARCHAR,
    password_reset_token VARCHAR,
    password_reset_expires TIMESTAMP,
    firebase_uid VARCHAR UNIQUE,
    
    -- Security tracking
    last_login TIMESTAMP,
    login_attempts INTEGER DEFAULT 0,
    locked_until TIMESTAMP,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### Sessions Table

```sql
CREATE TABLE sessions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER,
    token VARCHAR UNIQUE NOT NULL,
    ip_address VARCHAR,
    user_agent VARCHAR,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP,
    last_activity TIMESTAMP DEFAULT NOW()
);
```

## Email Templates

Email templates support both HTML and plain text formats.

### Verification Email

- Subject: "Verify Your ASF-Engine Account"
- Includes verification link
- Expires in 24 hours
- Branded with company colors

### Password Reset Email

- Subject: "Reset Your ASF-Engine Password"
- Includes reset link
- Expires in 1 hour
- Security warnings included

### Welcome Email

- Sent after email verification
- Feature overview
- Getting started guide

## Troubleshooting

### Issue: "DATABASE_URL environment variable must be set"

**Solution:** Create `.env` file with valid DATABASE_URL

```env
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
```

### Issue: "JWT_SECRET_KEY must be at least 32 characters long"

**Solution:** Generate a secure secret key:

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### Issue: Email verification not working

**Solutions:**
1. Check SMTP credentials in `.env`
2. Verify SMTP_USER and SMTP_PASSWORD are correct
3. For Gmail: Use App Password, not regular password
4. Check firewall/security settings

### Issue: Firebase authentication failing

**Solutions:**
1. Verify Firebase credentials are correct
2. Enable Email/Password auth in Firebase Console
3. Check API key permissions
4. Ensure Firebase project is active

## Best Practices

### Production Deployment

1. **Use strong JWT secret**
   ```bash
   # Generate secure key
   JWT_SECRET_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(32))")
   ```

2. **Enable HTTPS**
   - Use SSL/TLS certificates
   - Configure BASE_URL with https://

3. **Configure CORS properly**
   ```env
   CORS_ORIGINS=https://yourdomain.com,https://app.yourdomain.com
   ```

4. **Use production database**
   - PostgreSQL (not SQLite)
   - Regular backups
   - Connection pooling

5. **Secure email configuration**
   - Use app-specific passwords
   - Enable 2FA on email account
   - Monitor email sending limits

### Security Checklist

- [ ] JWT_SECRET_KEY is 32+ characters and secure
- [ ] DATABASE_URL uses strong password
- [ ] SMTP credentials are secure (app password)
- [ ] Firebase credentials are restricted to your domain
- [ ] HTTPS enabled in production
- [ ] CORS configured for specific domains only
- [ ] Regular database backups enabled
- [ ] Session timeout configured appropriately
- [ ] Account lockout enabled
- [ ] Email verification required for sensitive actions

## Testing

### Manual Testing

1. **Sign Up Flow**
   - Create new account
   - Check email for verification link
   - Verify email
   - Login with new account

2. **Login Flow**
   - Login with correct credentials
   - Try wrong password (should fail)
   - Try 6 times (should lock account)
   - Wait 30 minutes (should unlock)

3. **Password Reset**
   - Click "Forgot Password"
   - Enter email
   - Check email for reset link
   - Reset password
   - Login with new password

4. **Role-Based Access**
   - Login as regular user
   - Check available features
   - Login as admin
   - Verify admin features visible

### Automated Testing

```bash
# Run backend tests
pytest backend/tests/

# Test database connectivity
python scripts/init_db.py

# Test email service
python -c "from auth.email_service import EmailService; EmailService().send_verification_email('test@test.com', 'token123', 'Test User')"
```

## Support

For issues or questions:
- GitHub Issues: https://github.com/ravigohel142996/ASF-Engine/issues
- Documentation: README.md
- Security Issues: Report privately to maintainers

## License

MIT License - See LICENSE file for details
