from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from enum import Enum

db = SQLAlchemy()

class ProspectStatus(Enum):
    DISCOVERED = "discovered"
    QUALIFIED = "qualified"
    MESSAGED = "messaged"
    RESPONDED = "responded"
    CONVERTED = "converted"
    REJECTED = "rejected"

class CampaignStatus(Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"

class Prospect(db.Model):
    __tablename__ = 'prospects'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    full_name = db.Column(db.String(200))
    followers = db.Column(db.Integer, nullable=False)
    following = db.Column(db.Integer)
    posts_count = db.Column(db.Integer)
    engagement_rate = db.Column(db.Float)
    bio = db.Column(db.Text)
    coach_score = db.Column(db.Float, default=0.0)
    value_score = db.Column(db.Float, default=0.0)
    niche = db.Column(db.String(100))
    status = db.Column(db.Enum(ProspectStatus), default=ProspectStatus.DISCOVERED)
    dm_sent = db.Column(db.Boolean, default=False)
    dm_sent_at = db.Column(db.DateTime)
    response_received = db.Column(db.Boolean, default=False)
    response_received_at = db.Column(db.DateTime)
    profile_url = db.Column(db.String(500))
    profile_pic_url = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    messages = db.relationship('Message', backref='prospect', lazy=True)

class Campaign(db.Model):
    __tablename__ = 'campaigns'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    hashtags = db.Column(db.Text)  # JSON string of hashtags
    target_accounts = db.Column(db.Text)  # JSON string of target accounts
    instagram_account_id = db.Column(db.Integer, db.ForeignKey('instagram_accounts.id'), nullable=True)  # Link to Instagram account
    status = db.Column(db.Enum(CampaignStatus), default=CampaignStatus.ACTIVE)
    messages_sent = db.Column(db.Integer, default=0)
    responses_received = db.Column(db.Integer, default=0)
    conversions = db.Column(db.Integer, default=0)
    daily_limit = db.Column(db.Integer, default=50)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    messages = db.relationship('Message', backref='campaign', lazy=True)

class Message(db.Model):
    __tablename__ = 'messages'
    
    id = db.Column(db.Integer, primary_key=True)
    prospect_id = db.Column(db.Integer, db.ForeignKey('prospects.id'), nullable=False)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaigns.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    sent_at = db.Column(db.DateTime, default=datetime.utcnow)
    response_at = db.Column(db.DateTime)
    response_content = db.Column(db.Text)
    message_type = db.Column(db.String(50), default='initial')  # initial, follow_up
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class InstagramAccount(db.Model):
    __tablename__ = 'instagram_accounts'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    session_id = db.Column(db.Text, nullable=False)  # Instagram session ID for Apify
    is_active = db.Column(db.Boolean, default=True)
    daily_messages_sent = db.Column(db.Integer, default=0)
    daily_limit = db.Column(db.Integer, default=40)  # Max messages per day for this account
    last_activity = db.Column(db.DateTime)
    last_reset_date = db.Column(db.Date, default=datetime.utcnow().date)  # Track daily limit resets
    account_status = db.Column(db.String(50), default='active')  # active, suspended, limited
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    campaigns = db.relationship('Campaign', backref='instagram_account', lazy=True)
