#!/usr/bin/env python3
"""
Database initialization script to handle schema updates
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from flask import Flask
from models import db, InstagramAccount, Campaign, Prospect, Message, User

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///coach_outreach.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

def init_database():
    """Initialize database with proper schema"""
    with app.app_context():
        db.drop_all()
        print("Dropped all existing tables")
        
        db.create_all()
        print("Created all tables with updated schema")
        
        inspector = db.inspect(db.engine)
        columns = inspector.get_columns('instagram_accounts')
        column_names = [col['name'] for col in columns]
        
        if 'session_id' in column_names:
            print("✅ InstagramAccount table created successfully with session_id column")
        else:
            print("❌ ERROR: session_id column missing from InstagramAccount table")
            return False
            
        print("Database initialization completed successfully!")
        return True

if __name__ == '__main__':
    success = init_database()
    sys.exit(0 if success else 1)
