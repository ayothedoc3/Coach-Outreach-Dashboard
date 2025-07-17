from sqlalchemy import Boolean, Column, Integer, String, DateTime, Enum, Float, Text, Date, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum as PyEnum

from app.database import Base

class ProspectStatus(PyEnum):
    DISCOVERED = "discovered"
    QUALIFIED = "qualified"
    MESSAGED = "messaged"
    RESPONDED = "responded"
    CONVERTED = "converted"
    REJECTED = "rejected"

class CampaignStatus(PyEnum):
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"

class Prospect(Base):
    __tablename__ = 'prospects'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(100), unique=True, nullable=False)
    full_name = Column(String(200))
    followers = Column(Integer, nullable=False)
    following = Column(Integer)
    posts_count = Column(Integer)
    engagement_rate = Column(Float)
    bio = Column(Text)
    coach_score = Column(Float, default=0.0)
    value_score = Column(Float, default=0.0)
    niche = Column(String(100))
    status = Column(Enum(ProspectStatus), default=ProspectStatus.DISCOVERED)
    dm_sent = Column(Boolean, default=False)
    dm_sent_at = Column(DateTime)
    response_received = Column(Boolean, default=False)
    response_received_at = Column(DateTime)
    profile_url = Column(String(500))
    profile_pic_url = Column(String(500))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    messages = relationship('Message', back_populates='prospect')

class Campaign(Base):
    __tablename__ = 'campaigns'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    hashtags = Column(Text)  # JSON string of hashtags
    target_accounts = Column(Text)  # JSON string of target accounts
    instagram_account_id = Column(Integer, ForeignKey('instagram_accounts.id'), nullable=True)  # Link to Instagram account
    status = Column(Enum(CampaignStatus), default=CampaignStatus.ACTIVE)
    messages_sent = Column(Integer, default=0)
    responses_received = Column(Integer, default=0)
    conversions = Column(Integer, default=0)
    daily_limit = Column(Integer, default=50)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    messages = relationship('Message', back_populates='campaign')
    instagram_account = relationship('InstagramAccount', back_populates='campaigns')

class Message(Base):
    __tablename__ = 'messages'
    
    id = Column(Integer, primary_key=True)
    prospect_id = Column(Integer, ForeignKey('prospects.id'), nullable=False)
    campaign_id = Column(Integer, ForeignKey('campaigns.id'), nullable=False)
    content = Column(Text, nullable=False)
    sent_at = Column(DateTime, default=datetime.utcnow)
    response_at = Column(DateTime)
    response_content = Column(Text)
    message_type = Column(String(50), default='initial')  # initial, follow_up
    created_at = Column(DateTime, default=datetime.utcnow)

    prospect = relationship('Prospect', back_populates='messages')
    campaign = relationship('Campaign', back_populates='messages')

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(80), unique=True, nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    password_hash = Column(String(128))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class InstagramAccount(Base):
    __tablename__ = 'instagram_accounts'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(100), unique=True, nullable=False)
    session_id = Column(Text, nullable=False)  # Instagram session ID for Apify
    is_active = Column(Boolean, default=True)
    daily_messages_sent = Column(Integer, default=0)
    daily_limit = Column(Integer, default=40)  # Max messages per day for this account
    last_activity = Column(DateTime)
    last_reset_date = Column(Date, default=datetime.utcnow().date)  # Track daily limit resets
    account_status = Column(String(50), default='active')  # active, suspended, limited
    created_at = Column(DateTime, default=datetime.utcnow)
    
    campaigns = relationship('Campaign', back_populates='instagram_account')

class DeploymentStatus(PyEnum):
    PENDING = "pending"
    BUILDING = "building"
    DEPLOYING = "deploying"
    RUNNING = "running"
    FAILED = "failed"
    STOPPED = "stopped"

class CoolifyConfig(Base):
    __tablename__ = 'coolify_configs'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    api_url = Column(String(500), nullable=False)  # Coolify instance URL
    api_token = Column(Text, nullable=False)  # Coolify API token
    team_id = Column(String(100))  # Coolify team ID
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    deployments = relationship('Deployment', back_populates='coolify_config')

class Deployment(Base):
    __tablename__ = 'deployments'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    github_url = Column(String(500), nullable=False)
    project_type = Column(String(50), default='unknown')  # nodejs, python, docker, etc.
    coolify_config_id = Column(Integer, ForeignKey('coolify_configs.id'), nullable=False)
    coolify_app_id = Column(String(100))  # Coolify application ID
    status = Column(Enum(DeploymentStatus), default=DeploymentStatus.PENDING)
    build_logs = Column(Text)
    deployment_url = Column(String(500))
    environment_variables = Column(Text)  # JSON string of env vars
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    coolify_config = relationship('CoolifyConfig', back_populates='deployments')
