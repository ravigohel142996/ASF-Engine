"""
Database Initialization Script
Run this to create all necessary tables and seed initial data
"""
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.database import init_db, SessionLocal, create_user
from backend.auth import get_password_hash
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def create_default_admin():
    """Create default admin user if it doesn't exist"""
    db = SessionLocal()
    
    try:
        from backend.database import get_user_by_email
        
        # Check if admin exists
        admin_email = os.getenv('DEMO_EMAIL', 'admin@test.com')
        existing_admin = get_user_by_email(db, admin_email)
        
        if not existing_admin:
            print(f"Creating default admin user: {admin_email}")
            admin = create_user(
                db,
                email=admin_email,
                hashed_password=get_password_hash(os.getenv('DEMO_PASSWORD', '1234')),
                full_name="Admin User"
            )
            admin.role = "admin"
            admin.email_verified = True
            admin.is_admin = True
            db.commit()
            print(f"✅ Admin user created: {admin_email}")
        else:
            print(f"ℹ️  Admin user already exists: {admin_email}")
    
    except Exception as e:
        print(f"❌ Error creating admin user: {e}")
        db.rollback()
    
    finally:
        db.close()


def main():
    """Main initialization function"""
    print("=" * 60)
    print("ASF-Engine Database Initialization")
    print("=" * 60)
    
    # Check if DATABASE_URL is set
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("❌ ERROR: DATABASE_URL environment variable not set")
        print("Please create a .env file with DATABASE_URL configured")
        return
    
    print(f"Database URL: {database_url[:30]}...")
    
    # Initialize database
    print("\n📊 Creating database tables...")
    try:
        init_db()
        print("✅ Database tables created successfully")
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        return
    
    # Create default admin
    print("\n👤 Setting up admin user...")
    create_default_admin()
    
    print("\n" + "=" * 60)
    print("✅ Database initialization complete!")
    print("=" * 60)
    print("\nYou can now start the application:")
    print("  Streamlit: streamlit run app.py")
    print("  Backend:   python backend/main.py")
    print()


if __name__ == "__main__":
    main()
