import time
import random
import json
from datetime import datetime, timedelta, date
from typing import List, Dict, Optional
from apify_client import ApifyClient
import openai
import os
from models import db, Prospect, Campaign, Message, ProspectStatus, InstagramAccount
from message_templates import MessageTemplates

class ApifyInstagramBot:
    
    def __init__(self, account_id: int = None, session_id: str = None):
        """
        Initialize bot with either an account_id (preferred) or session_id (fallback)
        """
        if account_id:
            self.account = InstagramAccount.query.get(account_id)
            if not self.account:
                raise ValueError(f"Instagram account with ID {account_id} not found")
            if not self.account.is_active:
                raise ValueError(f"Instagram account {self.account.username} is not active")
            self.session_id = self.account.session_id
            self.account_id = account_id
        elif session_id:
            self.session_id = session_id
            self.account = None
            self.account_id = None
        else:
            raise ValueError("Either account_id or session_id must be provided")
        
        self.message_delay = int(os.getenv('MESSAGE_DELAY', 60))
        self.openai_client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY')) if os.getenv('OPENAI_API_KEY') else None
        
        apify_token = os.getenv('APIFY_API_TOKEN')
        if not apify_token:
            raise ValueError("APIFY_API_TOKEN environment variable is required")
        
        self.apify_client = ApifyClient(apify_token)
        self.actor_id = os.getenv('APIFY_ACTOR_ID', 'deepanshusharm/instagram-dms-automation')
        
    @staticmethod
    def select_best_available_account() -> Optional[InstagramAccount]:
        """
        Select the best available Instagram account based on daily limits and status
        """
        today = date.today()
        
        accounts_to_reset = InstagramAccount.query.filter(
            InstagramAccount.last_reset_date < today,
            InstagramAccount.is_active == True
        ).all()
        
        for account in accounts_to_reset:
            account.daily_messages_sent = 0
            account.last_reset_date = today
        
        db.session.commit()
        
        available_account = InstagramAccount.query.filter(
            InstagramAccount.is_active == True,
            InstagramAccount.account_status == 'active',
            InstagramAccount.daily_messages_sent < InstagramAccount.daily_limit
        ).order_by(InstagramAccount.daily_messages_sent.asc()).first()
        
        return available_account
    
    @staticmethod
    def get_account_daily_remaining(account_id: int) -> int:
        """
        Get remaining daily message limit for an account
        """
        account = InstagramAccount.query.get(account_id)
        if not account:
            return 0
        
        today = date.today()
        if account.last_reset_date < today:
            return account.daily_limit
        
        return max(0, account.daily_limit - account.daily_messages_sent)
    
    def update_account_usage(self, messages_sent: int):
        """
        Update the account's daily message count
        """
        if self.account:
            today = date.today()
            if self.account.last_reset_date < today:
                self.account.daily_messages_sent = 0
                self.account.last_reset_date = today
            
            self.account.daily_messages_sent += messages_sent
            self.account.last_activity = datetime.utcnow()
            db.session.commit()

    def analyze_bio_with_ai(self, bio: str) -> Dict:
        """Use OpenAI to analyze bio and score prospect"""
        if not self.openai_client or not bio:
            return {'coach_score': 0.0, 'value_score': 0.0, 'niche': 'general'}
        
        try:
            prompt = f"""
            Analyze this Instagram bio for a potential coaching prospect:
            
            Bio: "{bio}"
            
            Rate on a scale of 1-10:
            1. Coach Score: How likely is this person a professional coach?
            2. Value Score: How likely do they offer high-value ($1000+) programs?
            3. Niche: What coaching niche (business, life, fitness, mindset, general)?
            
            Respond in JSON format:
            {{"coach_score": 8.5, "value_score": 7.2, "niche": "business"}}
            """
            
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=100,
                temperature=0.3
            )
            
            result = json.loads(response.choices[0].message.content)
            return {
                'coach_score': float(result.get('coach_score', 0.0)),
                'value_score': float(result.get('value_score', 0.0)),
                'niche': result.get('niche', 'general')
            }
            
        except Exception as e:
            print(f"AI analysis error: {str(e)}")
            return {'coach_score': 0.0, 'value_score': 0.0, 'niche': 'general'}
    
    def send_dm_batch(self, usernames: List[str], message: str) -> Dict[str, bool]:
        """Send DMs to a batch of users using Apify actor"""
        if not usernames:
            return {}
        
        batch_size = min(5, len(usernames))
        batch_usernames = usernames[:batch_size]
        
        try:
            run_input = {
                "sessionid": self.session_id,
                "target_usernames": batch_usernames,
                "message": message,
                "delay_between_messages": self.message_delay,
                "proxy": {
                    "useApifyProxy": True,
                    "apifyProxyGroups": ["RESIDENTIAL"]
                },
                "max_users": batch_size
            }
            
            print(f"Starting Apify actor run for {len(batch_usernames)} users...")
            run = self.apify_client.actor(self.actor_id).call(run_input=run_input)
            
            results = {}
            if run and run.get('status') == 'SUCCEEDED':
                dataset_items = self.apify_client.dataset(run['defaultDatasetId']).list_items().items
                
                for item in dataset_items:
                    username = item.get('username')
                    status = item.get('status')
                    if username:
                        results[username] = status == 'success'
                        if status == 'success':
                            print(f"Message sent successfully to {username}")
                        else:
                            print(f"Failed to send message to {username}: {status}")
            else:
                print(f"Apify actor run failed: {run.get('status') if run else 'No run data'}")
                for username in batch_usernames:
                    results[username] = False
            
            return results
            
        except Exception as e:
            print(f"Error in Apify actor run: {str(e)}")
            return {username: False for username in batch_usernames}
    
    def run_campaign(self, campaign_id: int):
        """Run a campaign with safety limits using Apify"""
        try:
            campaign = Campaign.query.get(campaign_id)
            if not campaign or campaign.status != 'active':
                print(f"Campaign {campaign_id} is not active or not found")
                return
            
            if campaign.instagram_account_id:
                if self.account_id != campaign.instagram_account_id:
                    print(f"Switching to campaign-specific account {campaign.instagram_account_id}")
                    self.account = InstagramAccount.query.get(campaign.instagram_account_id)
                    if not self.account or not self.account.is_active:
                        print(f"Campaign account {campaign.instagram_account_id} is not available")
                        return
                    self.session_id = self.account.session_id
                    self.account_id = self.account.id
            elif not self.account:
                self.account = self.select_best_available_account()
                if not self.account:
                    print("No available Instagram accounts found")
                    return
                self.session_id = self.account.session_id
                self.account_id = self.account.id
                print(f"Auto-selected account: {self.account.username}")
            
            remaining_limit = self.get_account_daily_remaining(self.account_id)
            if remaining_limit <= 0:
                print(f"Daily limit reached for account {self.account.username}")
                return
            
            today = datetime.now().date()
            campaign_messages_today = Message.query.filter(
                Message.campaign_id == campaign_id,
                db.func.date(Message.sent_at) == today
            ).count()
            
            campaign_remaining = campaign.daily_limit - campaign_messages_today
            remaining_limit = min(remaining_limit, campaign_remaining)
            
            if remaining_limit <= 0:
                print(f"Daily limit reached for campaign {campaign_id}")
                return
            
            prospects = Prospect.query.filter(
                Prospect.status == ProspectStatus.QUALIFIED,
                Prospect.dm_sent == False
            ).limit(remaining_limit).all()
            
            if not prospects:
                print("No qualified prospects to message")
                return
            
            print(f"Found {len(prospects)} qualified prospects to message")
            print(f"Using account: {self.account.username} (remaining limit: {remaining_limit})")
            
            messages_sent = 0
            batch_size = 5
            
            for i in range(0, len(prospects), batch_size):
                if messages_sent >= remaining_limit:
                    break
                
                batch_prospects = prospects[i:i + batch_size]
                usernames = [p.username for p in batch_prospects]
                
                prospect_data = {
                    'username': batch_prospects[0].username,
                    'full_name': batch_prospects[0].full_name,
                    'niche': batch_prospects[0].niche,
                    'followers': batch_prospects[0].followers
                }
                
                message_content = MessageTemplates.get_personalized_message(prospect_data)
                
                print(f"Sending batch of {len(usernames)} messages...")
                results = self.send_dm_batch(usernames, message_content)
                
                for prospect in batch_prospects:
                    if messages_sent >= remaining_limit:
                        break
                    
                    success = results.get(prospect.username, False)
                    
                    if success:
                        prospect.dm_sent = True
                        prospect.dm_sent_at = datetime.utcnow()
                        prospect.status = ProspectStatus.MESSAGED
                        
                        message = Message(
                            prospect_id=prospect.id,
                            campaign_id=campaign_id,
                            content=message_content
                        )
                        db.session.add(message)
                        
                        campaign.messages_sent += 1
                        messages_sent += 1
                        
                        print(f"Successfully processed message for {prospect.username}")
                    else:
                        print(f"Failed to send message to {prospect.username}")
                
                if i + batch_size < len(prospects) and messages_sent < remaining_limit:
                    delay = random.uniform(self.message_delay * 2, self.message_delay * 3)
                    print(f"Waiting {delay:.1f} seconds before next batch...")
                    time.sleep(delay)
            
            self.update_account_usage(messages_sent)
            
            db.session.commit()
            print(f"Campaign completed. Sent {messages_sent} messages using account {self.account.username}.")
            
        except Exception as e:
            print(f"Campaign error: {str(e)}")
            db.session.rollback()
            raise
