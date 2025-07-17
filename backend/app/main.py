from fastapi import FastAPI, Depends, HTTPException, status, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta, date
from typing import Optional, List
import os
import sys
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import Base, engine, Prospect, Campaign, Message, User, ProspectStatus, CampaignStatus, InstagramAccount, CoolifyConfig, Deployment, DeploymentStatus
from database import get_db
from schemas import *
from auth import authenticate_user, create_access_token, get_current_user, ACCESS_TOKEN_EXPIRE_MINUTES
from instagram_bot import ApifyInstagramBot
from message_templates import MessageTemplates
from coolify_service import CoolifyService

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Coach Outreach Dashboard API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/healthz")
def healthz():
    return {"status": "healthy"}

@app.get("/api/healthz")
def api_healthz():
    return {"status": "healthy"}

@app.post("/api/auth/login", response_model=Token)
async def login(user_login: UserLogin, db: Session = Depends(get_db)):
    user = authenticate_user(db, user_login.username, user_login.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/api/dashboard/stats", response_model=DashboardStats)
async def dashboard_stats(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        total_prospects = db.query(Prospect).count()
        qualified_prospects = db.query(Prospect).filter(Prospect.status == ProspectStatus.QUALIFIED).count()
        messages_sent = db.query(Message).count()
        responses_received = db.query(Prospect).filter(Prospect.response_received == True).count()
        
        conversion_rate = 0.0
        if messages_sent > 0:
            conversions = db.query(Message).filter(Message.is_conversion == True).count()
            conversion_rate = (conversions / messages_sent) * 100
        
        active_campaigns = db.query(Campaign).filter(Campaign.status == CampaignStatus.ACTIVE).count()
        
        return DashboardStats(
            total_prospects=total_prospects,
            qualified_prospects=qualified_prospects,
            messages_sent=messages_sent,
            responses_received=responses_received,
            conversion_rate=round(conversion_rate, 2),
            active_campaigns=active_campaigns
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/prospects")
async def get_prospects(
    page: int = 1,
    per_page: int = 20,
    status: Optional[str] = None,
    niche: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        query = db.query(Prospect)
        
        if status:
            try:
                status_enum = ProspectStatus(status)
                query = query.filter(Prospect.status == status_enum)
            except ValueError:
                pass
        
        if niche:
            query = query.filter(Prospect.niche.ilike(f'%{niche}%'))
        
        total = query.count()
        prospects = query.order_by(Prospect.created_at.desc()).offset((page - 1) * per_page).limit(per_page).all()
        
        pages = (total + per_page - 1) // per_page
        
        return {
            'prospects': [ProspectResponse.from_orm(p) for p in prospects],
            'total': total,
            'pages': pages,
            'current_page': page
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/campaigns", response_model=List[CampaignResponse])
async def get_campaigns(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        campaigns = db.query(Campaign).order_by(Campaign.created_at.desc()).all()
        return [CampaignResponse.from_orm(c) for c in campaigns]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/campaigns", response_model=CampaignResponse)
async def create_campaign(
    campaign: CampaignCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        db_campaign = Campaign(**campaign.dict())
        db.add(db_campaign)
        db.commit()
        db.refresh(db_campaign)
        return CampaignResponse.from_orm(db_campaign)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

async def run_campaign_background(campaign_id: int, db: Session):
    try:
        campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
        if campaign and campaign.instagram_account_id:
            bot = ApifyInstagramBot(account_id=campaign.instagram_account_id)
        else:
            best_account = ApifyInstagramBot.select_best_available_account()
            if best_account:
                bot = ApifyInstagramBot(account_id=best_account.id)
            else:
                instagram_session_id = os.getenv('INSTAGRAM_SESSION_ID')
                if instagram_session_id:
                    bot = ApifyInstagramBot(session_id=instagram_session_id)
                else:
                    print("No Instagram accounts available and INSTAGRAM_SESSION_ID not set")
                    return
        
        bot.run_campaign(campaign_id)
    except Exception as e:
        print(f"Campaign error: {str(e)}")

@app.post("/api/campaigns/{campaign_id}/start")
async def start_campaign(
    campaign_id: int,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
        if not campaign:
            raise HTTPException(status_code=404, detail="Campaign not found")
        
        if campaign.status == CampaignStatus.ACTIVE:
            raise HTTPException(status_code=400, detail="Campaign is already active")
        
        campaign.status = CampaignStatus.ACTIVE
        db.commit()
        
        background_tasks.add_task(run_campaign_background, campaign_id, db)
        
        return {"message": "Campaign started successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/campaigns/{campaign_id}/pause")
async def pause_campaign(
    campaign_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
        if not campaign:
            raise HTTPException(status_code=404, detail="Campaign not found")
        
        campaign.status = CampaignStatus.PAUSED
        db.commit()
        return {"message": "Campaign paused successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/scrape/hashtag")
async def scrape_hashtag(
    request: HashtagScrapeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        hashtag = request.hashtag
        max_posts = request.max_posts
        
        if not hashtag:
            raise HTTPException(status_code=400, detail="Hashtag is required")
        
        bot = ApifyInstagramBot()
        prospects = bot.scrape_hashtag(hashtag, max_posts)
        
        saved_count = 0
        for prospect_data in prospects:
            existing = db.query(Prospect).filter(Prospect.username == prospect_data['username']).first()
            if not existing:
                prospect = Prospect(**prospect_data)
                db.add(prospect)
                saved_count += 1
        
        db.commit()
        
        return {
            'message': f'Scraped {len(prospects)} prospects, saved {saved_count} new ones',
            'total_scraped': len(prospects),
            'new_prospects': saved_count
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/prospects/{prospect_id}/send-message")
async def send_message_to_prospect(
    prospect_id: int,
    request: MessageSendRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        prospect = db.query(Prospect).filter(Prospect.id == prospect_id).first()
        if not prospect:
            raise HTTPException(status_code=404, detail="Prospect not found")
        
        if prospect.dm_sent:
            raise HTTPException(status_code=400, detail="Message already sent to this prospect")
        
        prospect_data = {
            'username': prospect.username,
            'full_name': prospect.full_name,
            'niche': prospect.niche,
            'followers': prospect.followers
        }
        
        message_content = MessageTemplates.get_personalized_message(prospect_data)
        
        bot = ApifyInstagramBot()
        success = bot.send_dm(prospect.username, message_content)
        
        if success:
            prospect.dm_sent = True
            prospect.dm_sent_at = datetime.utcnow()
            prospect.status = ProspectStatus.MESSAGED
            
            message = Message(
                prospect_id=prospect.id,
                campaign_id=1,
                content=message_content
            )
            db.add(message)
            db.commit()
            
            return {"message": "Message sent successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to send message")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    
@app.post("/api/send-message")
async def send_message(
    request: MessageSendRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        prospect = db.query(Prospect).filter(Prospect.id == request.prospect_id).first()
        if not prospect:
            raise HTTPException(status_code=404, detail="Prospect not found")
        
        bot = ApifyInstagramBot()
        success = bot.send_dm(prospect.username, request.message)
        
        if success:
            prospect.dm_sent = True
            prospect.dm_sent_at = datetime.utcnow()
            prospect.status = ProspectStatus.MESSAGED
            
            message = Message(
                prospect_id=prospect.id,
                campaign_id=1,
                content=request.message
            )
            db.add(message)
            db.commit()
            
            return {"message": "Message sent successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to send message")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/analytics/performance", response_model=AnalyticsData)
async def analytics_performance(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        total_prospects = db.query(Prospect).count()
        qualified_prospects = db.query(Prospect).filter(Prospect.status == ProspectStatus.QUALIFIED).count()
        messages_sent = db.query(Message).count()
        responses_received = db.query(Prospect).filter(Prospect.response_received == True).count()
        conversions = db.query(Message).filter(Message.is_conversion == True).count()
        
        conversion_rate = (conversions / messages_sent * 100) if messages_sent > 0 else 0
        response_rate = (responses_received / messages_sent * 100) if messages_sent > 0 else 0
        
        daily_stats = []
        for i in range(7):
            date_filter = datetime.utcnow().date() - timedelta(days=i)
            daily_messages = db.query(Message).filter(func.date(Message.sent_at) == date_filter).count()
            daily_stats.append({
                'date': date_filter.isoformat(),
                'messages_sent': daily_messages
            })
        
        return AnalyticsData(
            total_prospects=total_prospects,
            qualified_prospects=qualified_prospects,
            messages_sent=messages_sent,
            responses_received=responses_received,
            conversions=conversions,
            conversion_rate=round(conversion_rate, 2),
            response_rate=round(response_rate, 2),
            daily_stats=daily_stats
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/instagram-accounts", response_model=List[InstagramAccountResponse])
async def get_instagram_accounts(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        accounts = db.query(InstagramAccount).order_by(InstagramAccount.created_at.desc()).all()
        return [InstagramAccountResponse.from_orm(a) for a in accounts]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/instagram-accounts", response_model=InstagramAccountResponse)
async def create_instagram_account(
    account: InstagramAccountCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        existing = db.query(InstagramAccount).filter(InstagramAccount.username == account.username).first()
        if existing:
            raise HTTPException(status_code=400, detail="Account with this username already exists")
        
        db_account = InstagramAccount(**account.dict())
        db.add(db_account)
        db.commit()
        db.refresh(db_account)
        return InstagramAccountResponse.from_orm(db_account)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/instagram-accounts/{account_id}")
async def update_instagram_account(
    account_id: int,
    account_data: InstagramAccountCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        account = db.query(InstagramAccount).filter(InstagramAccount.id == account_id).first()
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")
        
        for field, value in account_data.dict(exclude_unset=True).items():
            setattr(account, field, value)
        
        db.commit()
        return {"message": f"Account {account.username} updated successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/instagram-accounts/{account_id}")
async def delete_instagram_account(
    account_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        account = db.query(InstagramAccount).filter(InstagramAccount.id == account_id).first()
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")
        
        active_campaigns = db.query(Campaign).filter(
            Campaign.instagram_account_id == account_id,
            Campaign.status == CampaignStatus.ACTIVE
        ).count()
        
        if active_campaigns > 0:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot delete account. It is being used by {active_campaigns} active campaign(s)"
            )
        
        username = account.username
        db.delete(account)
        db.commit()
        
        return {"message": f"Account {username} deleted successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/instagram-accounts/{account_id}/test")
async def test_instagram_account(
    account_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        bot = ApifyInstagramBot(account_id=account_id)
        
        account = db.query(InstagramAccount).filter(InstagramAccount.id == account_id).first()
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")
        
        account.last_activity = datetime.utcnow()
        db.commit()
        
        return {
            'status': 'success',
            'message': f'Account {account.username} session appears valid'
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Account test failed: {str(e)}"
        )

@app.get("/api/coolify/configs", response_model=List[CoolifyConfigResponse])
async def get_coolify_configs(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        configs = db.query(CoolifyConfig).filter(CoolifyConfig.is_active == True).all()
        return [CoolifyConfigResponse.from_orm(c) for c in configs]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/coolify/configs", response_model=CoolifyConfigResponse)
async def create_coolify_config(
    config: CoolifyConfigCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        db_config = CoolifyConfig(**config.dict())
        db.add(db_config)
        db.commit()
        db.refresh(db_config)
        return CoolifyConfigResponse.from_orm(db_config)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/deployments", response_model=List[DeploymentResponse])
async def get_deployments(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        deployments = db.query(Deployment).order_by(Deployment.created_at.desc()).all()
        return [DeploymentResponse.from_orm(d) for d in deployments]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/deployments", response_model=DeploymentResponse)
async def create_deployment(
    deployment: DeploymentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        coolify_config = db.query(CoolifyConfig).filter(CoolifyConfig.id == deployment.coolify_config_id).first()
        if not coolify_config:
            raise HTTPException(status_code=404, detail="Coolify config not found")
        
        coolify_service = CoolifyService(coolify_config.api_url, coolify_config.api_token)
        
        db_deployment = Deployment(**deployment.dict())
        db.add(db_deployment)
        db.commit()
        db.refresh(db_deployment)
        
        try:
            app_id = coolify_service.create_application(
                name=deployment.name,
                github_url=deployment.github_url,
                environment_variables=deployment.environment_variables
            )
            
            db_deployment.coolify_app_id = app_id
            db_deployment.status = DeploymentStatus.BUILDING
            db.commit()
            
        except Exception as deploy_error:
            db_deployment.status = DeploymentStatus.FAILED
            db.commit()
            raise HTTPException(status_code=500, detail=f"Deployment failed: {str(deploy_error)}")
        
        return DeploymentResponse.from_orm(db_deployment)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/deployments/{deployment_id}/status")
async def get_deployment_status(
    deployment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        deployment = db.query(Deployment).filter(Deployment.id == deployment_id).first()
        if not deployment:
            raise HTTPException(status_code=404, detail="Deployment not found")
        
        coolify_service = CoolifyService(deployment.coolify_config.api_url, deployment.coolify_config.api_token)
        status_info = coolify_service.get_deployment_status(deployment)
        return status_info
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/deployments/{deployment_id}/environment-variables")
async def update_deployment_env_vars(
    deployment_id: int,
    env_vars: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        deployment = db.query(Deployment).filter(Deployment.id == deployment_id).first()
        if not deployment:
            raise HTTPException(status_code=404, detail="Deployment not found")
        
        coolify_service = CoolifyService(deployment.coolify_config.api_url, deployment.coolify_config.api_token)
        if coolify_service.update_environment_variables(deployment, env_vars):
            return {"message": "Environment variables updated successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to update environment variables")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/deployments/{deployment_id}/detect-project")
async def detect_project_type(
    deployment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        deployment = db.query(Deployment).filter(Deployment.id == deployment_id).first()
        if not deployment:
            raise HTTPException(status_code=404, detail="Deployment not found")
        
        coolify_service = CoolifyService(deployment.coolify_config.api_url, deployment.coolify_config.api_token)
        project_type = coolify_service.detect_project_type(deployment.github_url)
        
        deployment.project_type = project_type
        db.commit()
        
        return {
            'project_type': project_type,
            'message': f'Detected project type: {project_type}'
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
