from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional

from . import schemas, models, crud
from .database import get_db

router = APIRouter()

SECRET_KEY = "your-secret-key"  # Change this in a real app
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

@router.post("/auth/login", response_model=schemas.Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    if not (form_data.username == 'admin' and form_data.password == 'admin'):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": form_data.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/prospects/", response_model=list[schemas.Prospect])
def read_prospects(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    prospects = crud.get_prospects(db, skip=skip, limit=limit)
    return prospects

@router.post("/prospects/", response_model=schemas.Prospect)
def create_prospect(prospect: schemas.ProspectCreate, db: Session = Depends(get_db)):
    return crud.create_prospect(db=db, prospect=prospect)

@router.get("/campaigns/", response_model=list[schemas.Campaign])
def read_campaigns(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    campaigns = crud.get_campaigns(db, skip=skip, limit=limit)
    return campaigns

@router.post("/campaigns/", response_model=schemas.Campaign)
def create_campaign(campaign: schemas.CampaignCreate, db: Session = Depends(get_db)):
    return crud.create_campaign(db=db, campaign=campaign)

@router.get("/messages/", response_model=list[schemas.Message])
def read_messages(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    messages = crud.get_messages(db, skip=skip, limit=limit)
    return messages

@router.post("/messages/", response_model=schemas.Message)
def create_message(message: schemas.MessageCreate, db: Session = Depends(get_db)):
    return crud.create_message(db=db, message=message)

@router.get("/instagram-accounts/", response_model=list[schemas.InstagramAccount])
def read_instagram_accounts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    accounts = crud.get_instagram_accounts(db, skip=skip, limit=limit)
    return accounts

@router.post("/instagram-accounts/", response_model=schemas.InstagramAccount)
def create_instagram_account(account: schemas.InstagramAccountCreate, db: Session = Depends(get_db)):
    return crud.create_instagram_account(db=db, account=account)

@router.get("/coolify-configs/", response_model=list[schemas.CoolifyConfig])
def read_coolify_configs(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    configs = crud.get_coolify_configs(db, skip=skip, limit=limit)
    return configs

@router.post("/coolify-configs/", response_model=schemas.CoolifyConfig)
def create_coolify_config(config: schemas.CoolifyConfigCreate, db: Session = Depends(get_db)):
    return crud.create_coolify_config(db=db, config=config)

@router.get("/deployments/", response_model=list[schemas.Deployment])
def read_deployments(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    deployments = crud.get_deployments(db, skip=skip, limit=limit)
    return deployments

@router.post("/deployments/", response_model=schemas.Deployment)
def create_deployment(deployment: schemas.DeploymentCreate, db: Session = Depends(get_db)):
    return crud.create_deployment(db=db, deployment=deployment)
