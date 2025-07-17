#!/usr/bin/env python3
"""
Database initialization script for FastAPI
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models import Base, engine, User, InstagramAccount, CoolifyConfig, SessionLocal
from auth import get_password_hash

def init_database():
    """Initialize database with proper schema"""
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        if not db.query(User).filter(User.username == 'admin').first():
            admin_user = User(
                username='admin',
                email='admin@example.com',
                password_hash=get_password_hash('admin')
            )
            db.add(admin_user)
            db.commit()
            print("Created admin user with hashed password")
        
        print("Database initialized successfully")
        return True
    except Exception as e:
        print(f"Error initializing database: {e}")
        return False
    finally:
        db.close()

if __name__ == '__main__':
    success = init_database()
    sys.exit(0 if success else 1)
