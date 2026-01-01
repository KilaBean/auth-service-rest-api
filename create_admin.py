import sys
import os

# Add the project root to the python path so we can import 'app' modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app.models import User
from app.security import hash_password

def create_first_admin():
    db = SessionLocal()
    try:
        # 1. Check if this email already exists
        existing_user = db.query(User).filter(User.email == "admin@myapp.com").first()
        
        if existing_user:
            print("⚠️  Admin user already exists! No changes made.")
        else:
            # 2. Create the admin user
            admin_user = User(
                email="admin@myapp.com",
                hashed_password=hash_password("StrongAdminPass123"),
                role="admin"  # Manually setting the role to admin here
            )
            
            db.add(admin_user)
            db.commit()
            print("✅ Success! First admin user created.")
            print("   Email:    admin@myapp.com")
            print("   Password: StrongAdminPass123")
            
    except Exception as e:
        print(f"❌ Error creating admin: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_first_admin()