# ASF-Engine Quick Start Guide

This guide will help you get ASF-Engine up and running in minutes.

## Prerequisites

- Python 3.10 or higher
- PostgreSQL 12+ (or SQLite for testing)
- pip (Python package manager)

## Step 1: Clone the Repository

```bash
git clone https://github.com/ravigohel142996/ASF-Engine.git
cd ASF-Engine
```

## Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

## Step 3: Configure Environment

Create a `.env` file from the example:

```bash
cp .env.example .env
```

### Minimal Configuration (for testing)

Edit `.env` and set these required variables:

```env
# Database (SQLite for testing)
DATABASE_URL=sqlite:///./asf_engine.db

# JWT Secret (generate a secure key)
JWT_SECRET_KEY=your-very-long-secret-key-minimum-32-characters-required

# Demo credentials
DEMO_EMAIL=admin@test.com
DEMO_PASSWORD=1234
```

### Production Configuration

For production, use PostgreSQL:

```env
# PostgreSQL Database
DATABASE_URL=postgresql://username:password@localhost:5432/asf_engine

# JWT Secret (generate with: python -c "import secrets; print(secrets.token_urlsafe(32))")
JWT_SECRET_KEY=your-production-secret-key-32-chars-minimum

# Firebase (optional - for enterprise auth)
FIREBASE_API_KEY=your_firebase_api_key
FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
FIREBASE_PROJECT_ID=your-project-id

# Email (for verification & password reset)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password
BASE_URL=https://yourdomain.com
```

## Step 4: Initialize Database

Run the database initialization script:

```bash
python scripts/init_db.py
```

This will:
- Create all database tables
- Create a default admin user
- Set up the database schema

Expected output:
```
============================================================
ASF-Engine Database Initialization
============================================================
Database URL: sqlite:///./asf_engine.db...

📊 Creating database tables...
✅ Database tables created successfully

👤 Setting up admin user...
✅ Admin user created: admin@test.com

============================================================
✅ Database initialization complete!
============================================================
```

## Step 5: Start the Application

Start the Streamlit frontend:

```bash
streamlit run app.py
```

The application will open in your browser at `http://localhost:8501`

### (Optional) Start the Backend API

In a separate terminal, start the FastAPI backend:

```bash
python backend/main.py
```

The API will be available at `http://localhost:8000`
- Swagger docs: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Step 6: Login

1. Navigate to the login page
2. Use the demo credentials:
   - **Email:** `admin@test.com`
   - **Password:** `1234`
3. Click "Login"

You should now be logged in and see the main dashboard!

## Features to Try

### 1. Create a New User Account

1. Click on "Sign Up" tab
2. Enter your details
3. Create account
4. Check your email for verification link (if SMTP configured)

### 2. Test Password Reset

1. Click "Forgot Password?" on login page
2. Enter your email
3. Check your email for reset link (if SMTP configured)

### 3. Explore the Dashboard

- View real-time metrics
- Monitor system health
- Check alerts and notifications
- Generate failure predictions

### 4. Test Role-Based Access

- Login as admin to see admin features
- Create a regular user to see user-level features

## Troubleshooting

### Issue: ModuleNotFoundError

**Solution:** Install missing dependencies
```bash
pip install -r requirements.txt
```

### Issue: Database connection error

**Solution:** Check your DATABASE_URL in `.env`
```bash
# For SQLite (testing)
DATABASE_URL=sqlite:///./asf_engine.db

# For PostgreSQL (production)
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
```

### Issue: JWT_SECRET_KEY error

**Solution:** Generate a secure key
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Copy the output to your `.env` file:
```env
JWT_SECRET_KEY=<paste-generated-key-here>
```

### Issue: Email not sending

**Cause:** SMTP not configured or credentials invalid

**Solutions:**
1. For Gmail, use an App Password (not your regular password)
2. Enable "Less secure app access" or use OAuth2
3. Check SMTP credentials in `.env`
4. Test SMTP connection:
   ```bash
   python -c "from auth.email_service import EmailService; print('SMTP configured:', EmailService().is_configured)"
   ```

### Issue: Import errors

**Solution:** Make sure you're running from the project root directory
```bash
cd /path/to/ASF-Engine
python scripts/init_db.py
streamlit run app.py
```

## What's Next?

Now that you have ASF-Engine running:

1. **Read the full documentation:** [README.md](README.md)
2. **Learn about authentication:** [AUTHENTICATION.md](AUTHENTICATION.md)
3. **Check deployment guide:** [DEPLOYMENT.md](DEPLOYMENT.md)
4. **Review security practices:** [SECURITY.md](SECURITY.md)

## Getting Help

- **Documentation:** Check the docs in this repository
- **Issues:** Open an issue on GitHub
- **Security:** Report security issues privately to maintainers

## Production Deployment

Before deploying to production:

1. ✅ Use PostgreSQL (not SQLite)
2. ✅ Generate strong JWT_SECRET_KEY (32+ characters)
3. ✅ Configure SMTP for email
4. ✅ Set up Firebase (optional but recommended)
5. ✅ Enable HTTPS
6. ✅ Set ENVIRONMENT=production
7. ✅ Configure proper CORS_ORIGINS
8. ✅ Set up database backups
9. ✅ Review [SECURITY.md](SECURITY.md)

## Support

Need help? Here are your options:

- 📚 Read the documentation
- 🐛 Open an issue on GitHub
- 💬 Check existing issues for solutions
- 🔐 For security issues, contact maintainers privately

---

**Happy monitoring! 🤖**
