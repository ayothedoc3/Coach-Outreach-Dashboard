from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from models import ProspectStatus, CampaignStatus, DeploymentStatus

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class ProspectBase(BaseModel):
    username: str
    full_name: Optional[str] = None
    bio: Optional[str] = None
    followers: int = 0
    following: int = 0
    posts_count: Optional[int] = None
    engagement_rate: Optional[float] = None
    coach_score: float = 0.0
    value_score: float = 0.0
    niche: Optional[str] = None

class ProspectCreate(ProspectBase):
    pass

class ProspectResponse(ProspectBase):
    id: int
    status: ProspectStatus
    dm_sent: bool
    dm_sent_at: Optional[datetime] = None
    response_received: bool
    response_received_at: Optional[datetime] = None
    notes: Optional[str] = None
    posts_count: Optional[int] = None
    engagement_rate: Optional[float] = None
    profile_url: Optional[str] = None
    profile_pic_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class CampaignBase(BaseModel):
    name: str
    description: Optional[str] = None
    hashtags: Optional[str] = None
    target_accounts: Optional[str] = None
    daily_limit: int = 50
    instagram_account_id: Optional[int] = None

class CampaignCreate(CampaignBase):
    pass

class CampaignResponse(CampaignBase):
    id: int
    status: CampaignStatus
    messages_sent: int = 0
    responses_received: int = 0
    conversions: int = 0
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class MessageResponse(BaseModel):
    id: int
    prospect_id: int
    campaign_id: int
    content: str
    sent_at: datetime
    response_content: Optional[str] = None
    response_at: Optional[datetime] = None
    message_type: str = 'initial'
    is_conversion: bool = False

    class Config:
        from_attributes = True

class InstagramAccountBase(BaseModel):
    username: str
    session_id: str
    daily_limit: int = 50
    account_status: str = 'active'
    notes: Optional[str] = None

class InstagramAccountCreate(InstagramAccountBase):
    pass

class InstagramAccountResponse(InstagramAccountBase):
    id: int
    is_active: bool
    daily_messages_sent: int = 0
    last_reset_date: Optional[datetime] = None
    last_activity: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class CoolifyConfigBase(BaseModel):
    name: str
    api_url: str
    api_token: str

class CoolifyConfigCreate(CoolifyConfigBase):
    pass

class CoolifyConfigResponse(CoolifyConfigBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class DeploymentBase(BaseModel):
    name: str
    github_url: str
    coolify_config_id: int
    environment_variables: Optional[str] = None

class DeploymentCreate(DeploymentBase):
    pass

class DeploymentResponse(DeploymentBase):
    id: int
    project_type: Optional[str] = None
    coolify_app_id: Optional[str] = None
    status: DeploymentStatus
    deployment_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class DashboardStats(BaseModel):
    total_prospects: int
    qualified_prospects: int
    messages_sent: int
    responses_received: int
    conversion_rate: float
    active_campaigns: int

class AnalyticsData(BaseModel):
    total_prospects: int
    qualified_prospects: int
    messages_sent: int
    responses_received: int
    conversions: int
    conversion_rate: float
    response_rate: float
    daily_stats: List[dict]

class HashtagScrapeRequest(BaseModel):
    hashtag: str
    max_posts: int = 100

class MessageSendRequest(BaseModel):
    prospect_id: int
    message: str
