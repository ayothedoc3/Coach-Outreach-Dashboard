import time
import random
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from apify_client import ApifyClient
import openai
import os
from models import db, Prospect, Campaign, Message, ProspectStatus
from message_templates import MessageTemplates

class ApifyInstagramBot:
    
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.daily_message_limit = int(os.getenv('DAILY_MESSAGE_LIMIT', 50))
        self.message_delay = int(os.getenv('MESSAGE_DELAY', 60))
        self.openai_client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY')) if os.getenv('OPENAI_API_KEY') else None
        
        apify_token = os.getenv('APIFY_API_TOKEN')
        if not apify_token:
            raise ValueError("APIFY_API_TOKEN environment variable is required")
        
        self.apify_client = ApifyClient(apify_token)
        self.actor_id = os.getenv('APIFY_ACTOR_ID', 'deepanshusharm/instagram-dms-automation')
        
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
            
            today = datetime.now().date()
            messages_sent_today = Message.query.filter(
                Message.campaign_id == campaign_id,
                db.func.date(Message.sent_at) == today
            ).count()
            
            remaining_limit = self.daily_message_limit - messages_sent_today
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
            
            db.session.commit()
            print(f"Campaign completed. Sent {messages_sent} messages.")
            
        except Exception as e:
            print(f"Campaign error: {str(e)}")
            db.session.rollback()
            raise
