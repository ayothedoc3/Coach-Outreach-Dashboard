from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Boolean, Float, ForeignKey, Enum as SQLEnum, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
from enum import Enum
import os

DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///coach_outreach.db')
engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class ProspectStatus(Enum):
    DISCOVERED = "discovered"
    QUALIFIED = "qualified"
    MESSAGED = "messaged"
    RESPONDED = "responded"
    CONVERTED = "converted"
    REJECTED = "rejected"

class CampaignStatus(Enum):
    DRAFT = "draft"
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
    status = Column(SQLEnum(ProspectStatus), default=ProspectStatus.DISCOVERED)
    dm_sent = Column(Boolean, default=False)
    dm_sent_at = Column(DateTime)
    response_received = Column(Boolean, default=False)
    response_received_at = Column(DateTime)
    notes = Column(Text)
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
    hashtags = Column(Text)
    target_accounts = Column(Text)
    instagram_account_id = Column(Integer, ForeignKey('instagram_accounts.id'), nullable=True)
    status = Column(SQLEnum(CampaignStatus), default=CampaignStatus.ACTIVE)
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
    response_received_at = Column(DateTime)
    message_type = Column(String(50), default='initial')
    created_at = Column(DateTime, default=datetime.utcnow)
    is_conversion = Column(Boolean, default=False)
    
    prospect = relationship('Prospect', back_populates='messages')
    campaign = relationship('Campaign', back_populates='messages')

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(80), unique=True, nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime)

class InstagramAccount(Base):
    __tablename__ = 'instagram_accounts'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(100), unique=True, nullable=False)
    session_id = Column(Text, nullable=False)
    is_active = Column(Boolean, default=True)
    daily_messages_sent = Column(Integer, default=0)
    daily_limit = Column(Integer, default=40)
    last_activity = Column(DateTime)
    last_reset_date = Column(Date, default=datetime.utcnow().date)
    account_status = Column(String(50), default='active')
    created_at = Column(DateTime, default=datetime.utcnow)
    notes = Column(Text)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    campaigns = relationship('Campaign', back_populates='instagram_account')

class DeploymentStatus(Enum):
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
    api_url = Column(String(500), nullable=False)
    api_token = Column(Text, nullable=False)
    team_id = Column(String(100))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    deployments = relationship('Deployment', back_populates='coolify_config')

class Deployment(Base):
    __tablename__ = 'deployments'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    github_url = Column(String(500), nullable=False)
    project_type = Column(String(50), default='unknown')
    coolify_config_id = Column(Integer, ForeignKey('coolify_configs.id'), nullable=False)
    coolify_app_id = Column(String(100))
    status = Column(SQLEnum(DeploymentStatus), default=DeploymentStatus.PENDING)
    build_logs = Column(Text)
    deployment_url = Column(String(500))
    environment_variables = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    coolify_config = relationship('CoolifyConfig', back_populates='deployments')
