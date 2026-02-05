# Authentication System - Simple Local Mode

## Overview
The ASF-Engine now uses a simple local authentication system instead of Firebase. No external services, databases, or environment variables are required.

## Credentials
- **Email:** `admin@asf.com`
- **Password:** `123456`

## Features
- ✅ No Firebase required
- ✅ No database required  
- ✅ No environment variables required
- ✅ Works instantly on Streamlit Cloud
- ✅ Session management with 1-hour timeout
- ✅ Simple login/logout functionality

## Files Changed

### New Files
- `auth/simple_auth.py` - Simple authentication module with hardcoded credentials

### Modified Files
- `app.py` - Updated to use simple_auth instead of Firebase
- `pages/login.py` - Simplified login page with local authentication
- `pages/admin.py` - Updated to use simple_auth
- `pages/subscription.py` - Updated to use simple_auth
- `pages/reset_password.py` - Shows info message (feature not available)
- `pages/verify_email.py` - Shows info message (feature not available)
- `requirements.txt` - Removed Firebase, database, and crypto dependencies

## Removed Dependencies
- pyrebase4 (Firebase authentication)
- sqlalchemy (Database ORM)
- psycopg2-binary (PostgreSQL driver)
- alembic (Database migrations)
- python-jose (JWT tokens)
- passlib (Password hashing)
- python-dotenv (Environment variables)

## Usage

### Running Locally
```bash
streamlit run app.py
```

### Running on Streamlit Cloud
Just deploy the repository - no configuration needed!

### Login Process
1. Navigate to the login page (automatically if not authenticated)
2. Enter credentials (see above)
3. Click "🚀 Login"
4. Access the dashboard

### Logout
Click the "🚪 Logout" button in the top right of the dashboard.

## Security Note
This is a simple authentication system intended for development and demo purposes. The credentials are hardcoded in the source code. For production use, consider:
- Using environment variables or Streamlit secrets
- Implementing proper password hashing
- Adding rate limiting
- Using a proper authentication service

## Technical Details

### Session Management
- Sessions are stored in Streamlit's `session_state`
- Sessions expire after 1 hour of inactivity
- Login status is checked on every page load

### Authentication Flow
1. User submits email and password
2. `SimpleAuth.login()` compares credentials
3. If valid, sets session state with user data
4. User is granted access to protected pages
5. Session is maintained across page navigation

### Protected Pages
All pages check authentication status:
- If not logged in → redirect to login page
- If logged in → allow access
- If session expired → redirect to login page

## Testing
The authentication system has been tested with:
- ✅ Login with correct credentials
- ✅ Login with incorrect credentials
- ✅ Session state management
- ✅ Logout functionality
- ✅ Session expiry
- ✅ User data retrieval
- ✅ CodeQL security scan (0 issues)

## Support
For issues or questions, please open an issue on GitHub.
