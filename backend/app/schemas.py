from pydantic import BaseModel, Json
from typing import List, Optional
from datetime import datetime
from enum import Enum

class ProspectStatus(str, Enum):
    DISCOVERED = "discovered"
    QUALIFIED = "qualified"
    MESSAGED = "messaged"
    RESPONDED = "responded"
    CONVERTED = "converted"
    REJECTED = "rejected"

class CampaignStatus(str, Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"

class DeploymentStatus(str, Enum):
    PENDING = "pending"
    BUILDING = "building"
    DEPLOYING = "deploying"
    RUNNING = "running"
    FAILED = "failed"
    STOPPED = "stopped"

class ProspectBase(BaseModel):
    username: str
    full_name: Optional[str] = None
    followers: int
    following: Optional[int] = None
    posts_count: Optional[int] = None
    engagement_rate: Optional[float] = None
    bio: Optional[str] = None
    coach_score: Optional[float] = 0.0
    value_score: Optional[float] = 0.0
    niche: Optional[str] = None
    status: Optional[ProspectStatus] = ProspectStatus.DISCOVERED
    dm_sent: Optional[bool] = False
    dm_sent_at: Optional[datetime] = None
    response_received: Optional[bool] = False
    response_received_at: Optional[datetime] = None
    profile_url: Optional[str] = None
    profile_pic_url: Optional[str] = None

class ProspectCreate(ProspectBase):
    pass

class Prospect(ProspectBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class CampaignBase(BaseModel):
    name: str
    description: Optional[str] = None
    hashtags: Optional[Json] = None
    target_accounts: Optional[Json] = None
    instagram_account_id: Optional[int] = None
    status: Optional[CampaignStatus] = CampaignStatus.ACTIVE
    messages_sent: Optional[int] = 0
    responses_received: Optional[int] = 0
    conversions: Optional[int] = 0
    daily_limit: Optional[int] = 50

class CampaignCreate(CampaignBase):
    pass

class Campaign(CampaignBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class MessageBase(BaseModel):
    prospect_id: int
    campaign_id: int
    content: str
    message_type: Optional[str] = 'initial'

class MessageCreate(MessageBase):
    pass

class Message(MessageBase):
    id: int
    sent_at: datetime
    response_at: Optional[datetime] = None
    response_content: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class UserBase(BaseModel):
    username: str
    email: str
    is_active: Optional[bool] = True

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class InstagramAccountBase(BaseModel):
    username: str
    session_id: str
    is_active: Optional[bool] = True
    daily_limit: Optional[int] = 40
    account_status: Optional[str] = 'active'

class InstagramAccountCreate(InstagramAccountBase):
    pass

class InstagramAccount(InstagramAccountBase):
    id: int
    daily_messages_sent: int
    last_activity: Optional[datetime] = None
    last_reset_date: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True

class CoolifyConfigBase(BaseModel):
    name: str
    api_url: str
    api_token: str
    team_id: Optional[str] = None
    is_active: Optional[bool] = True

class CoolifyConfigCreate(CoolifyConfigBase):
    pass

class CoolifyConfig(CoolifyConfigBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class DeploymentBase(BaseModel):
    name: str
    github_url: str
    coolify_config_id: int
    environment_variables: Optional[Json] = None

class DeploymentCreate(DeploymentBase):
    pass

class Deployment(DeploymentBase):
    id: int
    project_type: Optional[str] = 'unknown'
    coolify_app_id: Optional[str] = None
    status: Optional[DeploymentStatus] = DeploymentStatus.PENDING
    build_logs: Optional[str] = None
    deployment_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class LoginRequest(BaseModel):
    username: str
    password: str
