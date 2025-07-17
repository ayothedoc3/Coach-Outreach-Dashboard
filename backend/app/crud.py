from sqlalchemy.orm import Session
from app import models, schemas

def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = pwd_context.hash(user.password)
    db_user = models.User(username=user.username, email=user.email, password_hash=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_prospects(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Prospect).offset(skip).limit(limit).all()

def create_prospect(db: Session, prospect: schemas.ProspectCreate):
    db_prospect = models.Prospect(**prospect.dict())
    db.add(db_prospect)
    db.commit()
    db.refresh(db_prospect)
    return db_prospect

def get_campaigns(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Campaign).offset(skip).limit(limit).all()

def create_campaign(db: Session, campaign: schemas.CampaignCreate):
    db_campaign = models.Campaign(**campaign.dict())
    db.add(db_campaign)
    db.commit()
    db.refresh(db_campaign)
    return db_campaign

def get_messages(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Message).offset(skip).limit(limit).all()

def create_message(db: Session, message: schemas.MessageCreate):
    db_message = models.Message(**message.dict())
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message

def get_instagram_accounts(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.InstagramAccount).offset(skip).limit(limit).all()

def create_instagram_account(db: Session, account: schemas.InstagramAccountCreate):
    db_account = models.InstagramAccount(**account.dict())
    db.add(db_account)
    db.commit()
    db.refresh(db_account)
    return db_account

def get_coolify_configs(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.CoolifyConfig).offset(skip).limit(limit).all()

def create_coolify_config(db: Session, config: schemas.CoolifyConfigCreate):
    db_config = models.CoolifyConfig(**config.dict())
    db.add(db_config)
    db.commit()
    db.refresh(db_config)
    return db_config

def get_deployments(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Deployment).offset(skip).limit(limit).all()

def create_deployment(db: Session, deployment: schemas.DeploymentCreate):
    db_deployment = models.Deployment(**deployment.dict())
    db.add(db_deployment)
    db.commit()
    db.refresh(db_deployment)
    return db_deployment
