import time
import random
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from selenium import webdriver
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import openai
import os
from models import db, Prospect, Campaign, Message, ProspectStatus
from message_templates import MessageTemplates

class InstagramBot:
    
    def __init__(self, username: str, password: str, headless: bool = True):
        self.username = username
        self.password = password
        self.headless = headless
        self.driver: Optional[WebDriver] = None
        self.daily_message_limit = int(os.getenv('DAILY_MESSAGE_LIMIT', 50))
        self.message_delay = int(os.getenv('MESSAGE_DELAY', 120))  # 2 minutes
        self.openai_client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY')) if os.getenv('OPENAI_API_KEY') else None
        
    def setup_driver(self):
        """Setup Chrome driver with appropriate options"""
        chrome_options = Options()
        if self.headless:
            chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
        
        self.driver = webdriver.Chrome(options=chrome_options)
        if self.driver:
            self.driver.implicitly_wait(10)
        
    def login(self) -> bool:
        """Login to Instagram"""
        if not self.driver:
            return False
            
        try:
            self.driver.get('https://www.instagram.com/accounts/login/')
            time.sleep(random.uniform(3, 5))
            
            username_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.NAME, 'username'))
            )
            password_input = self.driver.find_element(By.NAME, 'password')
            
            username_input.send_keys(self.username)
            time.sleep(random.uniform(1, 2))
            password_input.send_keys(self.password)
            time.sleep(random.uniform(1, 2))
            
            login_button = self.driver.find_element(By.XPATH, "//button[@type='submit']")
            login_button.click()
            
            time.sleep(random.uniform(5, 8))
            
            if 'instagram.com/accounts/login' not in self.driver.current_url:
                print("Login successful!")
                return True
            else:
                print("Login failed!")
                return False
                
        except Exception as e:
            print(f"Login error: {str(e)}")
            return False
    
    def scrape_hashtag_posts(self, hashtag: str, limit: int = 100) -> List[Dict]:
        """Scrape posts from a hashtag"""
        prospects = []
        
        if not self.driver:
            return prospects
        
        try:
            url = f'https://www.instagram.com/explore/tags/{hashtag}/'
            self.driver.get(url)
            time.sleep(random.uniform(3, 5))
            
            posts_collected = 0
            scroll_attempts = 0
            max_scroll_attempts = 20
            
            while posts_collected < limit and scroll_attempts < max_scroll_attempts:
                post_links = self.driver.find_elements(By.XPATH, "//a[contains(@href, '/p/')]")
                
                for link in post_links[posts_collected:]:
                    if posts_collected >= limit:
                        break
                        
                    try:
                        href = link.get_attribute('href')
                        if href and '/p/' in href:
                            prospect_data = self.scrape_post_author(href)
                            if prospect_data and self.is_qualified_prospect(prospect_data):
                                prospects.append(prospect_data)
                                posts_collected += 1
                                
                        time.sleep(random.uniform(1, 3))
                        
                    except Exception as e:
                        print(f"Error processing post: {str(e)}")
                        continue
                
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(random.uniform(2, 4))
                scroll_attempts += 1
                
        except Exception as e:
            print(f"Error scraping hashtag {hashtag}: {str(e)}")
            
        return prospects
    
    def scrape_post_author(self, post_url: str) -> Optional[Dict]:
        """Scrape author information from a post"""
        if not self.driver:
            return None
            
        try:
            self.driver.get(post_url)
            time.sleep(random.uniform(2, 4))
            
            username_element = self.driver.find_element(By.XPATH, "//a[contains(@href, '/') and not(contains(@href, '/p/'))]//span")
            username = username_element.text if username_element else None
            
            if not username:
                return None
                
            profile_data = self.scrape_profile(username)
            return profile_data
            
        except Exception as e:
            print(f"Error scraping post author: {str(e)}")
            return None
    
    def scrape_profile(self, username: str) -> Optional[Dict]:
        """Scrape profile information"""
        if not self.driver:
            return None
            
        try:
            profile_url = f'https://www.instagram.com/{username}/'
            self.driver.get(profile_url)
            time.sleep(random.uniform(3, 5))
            
            followers_element = self.driver.find_element(By.XPATH, "//a[contains(@href, '/followers/')]//span")
            followers_text = followers_element.get_attribute('title') or followers_element.text
            followers = self.parse_follower_count(followers_text)
            
            following_element = self.driver.find_element(By.XPATH, "//a[contains(@href, '/following/')]//span")
            following_text = following_element.text
            following = self.parse_follower_count(following_text)
            
            posts_element = self.driver.find_element(By.XPATH, "//div[contains(text(), 'posts')]//span")
            posts_count = self.parse_follower_count(posts_element.text)
            
            bio_element = None
            try:
                bio_element = self.driver.find_element(By.XPATH, "//div[@data-testid='user-bio']")
                bio = bio_element.text if bio_element else ""
            except:
                bio = ""
            
            full_name = ""
            try:
                name_element = self.driver.find_element(By.XPATH, "//span[@class='x1lliihq x1plvlek xryxfnj x1n2onr6 x193iq5w xeuugli x1fj9vlw x13faqbe x1vvkbs x1s928wv xhkezso x1gmr53x x1cpjm7i x1fgarty x1943h6x x1i0vuye xvs91rp xo1l8bm x5n08af x10wh9bi x1wdrske x8viiok x18hxmgj']")
                full_name = name_element.text if name_element else ""
            except:
                pass
            
            profile_pic_url = ""
            try:
                img_element = self.driver.find_element(By.XPATH, "//img[contains(@alt, 'profile picture')]")
                profile_pic_url = img_element.get_attribute('src') if img_element else ""
            except:
                pass
            
            return {
                'username': username,
                'full_name': full_name,
                'followers': followers,
                'following': following,
                'posts_count': posts_count,
                'bio': bio,
                'profile_url': profile_url,
                'profile_pic_url': profile_pic_url,
                'engagement_rate': self.calculate_engagement_rate(username),
                'coach_score': 0.0,
                'value_score': 0.0,
                'niche': self.determine_niche(bio)
            }
            
        except Exception as e:
            print(f"Error scraping profile {username}: {str(e)}")
            return None
    
    def parse_follower_count(self, text: str) -> int:
        """Parse follower count from text (handles K, M suffixes)"""
        if not text:
            return 0
            
        text = text.replace(',', '').replace(' ', '').lower()
        
        if 'k' in text:
            return int(float(text.replace('k', '')) * 1000)
        elif 'm' in text:
            return int(float(text.replace('m', '')) * 1000000)
        else:
            try:
                return int(text)
            except:
                return 0
    
    def calculate_engagement_rate(self, username: str) -> float:
        """Calculate engagement rate (simplified version)"""
        return random.uniform(1.0, 8.0)  # Mock engagement rate
    
    def determine_niche(self, bio: str) -> str:
        """Determine coaching niche from bio"""
        if not bio:
            return 'general'
            
        bio_lower = bio.lower()
        
        if any(word in bio_lower for word in ['business', 'entrepreneur', 'ceo', 'startup', 'sales']):
            return 'business'
        elif any(word in bio_lower for word in ['life', 'personal', 'transformation', 'growth']):
            return 'life'
        elif any(word in bio_lower for word in ['fitness', 'health', 'wellness', 'nutrition', 'workout']):
            return 'fitness'
        elif any(word in bio_lower for word in ['mindset', 'mental', 'psychology', 'confidence']):
            return 'mindset'
        else:
            return 'general'
    
    def is_qualified_prospect(self, prospect_data: Dict) -> bool:
        """Check if prospect meets qualification criteria"""
        if not prospect_data:
            return False
            
        if prospect_data.get('followers', 0) < 10000:
            return False
            
        bio = prospect_data.get('bio', '').lower()
        coaching_keywords = ['coach', 'coaching', 'mentor', 'consultant', 'trainer', 'guide']
        
        if not any(keyword in bio for keyword in coaching_keywords):
            return False
            
        value_keywords = ['premium', 'exclusive', '1-on-1', 'mastermind', 'program', 'course']
        has_value_indicators = any(keyword in bio for keyword in value_keywords)
        
        return has_value_indicators
    
    def analyze_bio_with_ai(self, bio: str) -> Dict:
        """Use OpenAI to analyze bio and score prospect"""
        if not self.openai_client or not bio:
            return {'coach_score': 0.0, 'value_score': 0.0, 'niche': 'general'}
        
        try:
            prompt = f"""
            Analyze this Instagram bio for a potential coaching prospect:
            
            Bio: "{bio}"
            
            Please provide:
            1. Coach Score (0-10): How likely is this person a professional coach?
            2. Value Score (0-10): How likely do they offer high-value ($1K+) programs?
            3. Niche: What type of coaching (business, life, fitness, mindset, general)?
            
            Respond in JSON format:
            {{"coach_score": 0.0, "value_score": 0.0, "niche": "category"}}
            """
            
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=150,
                temperature=0.3
            )
            
            result = json.loads(response.choices[0].message.content)
            return result
            
        except Exception as e:
            print(f"AI analysis error: {str(e)}")
            return {'coach_score': 0.0, 'value_score': 0.0, 'niche': 'general'}
    
    def send_dm(self, username: str, message: str) -> bool:
        """Send direct message to a user"""
        if not self.driver:
            return False
            
        try:
            profile_url = f'https://www.instagram.com/{username}/'
            self.driver.get(profile_url)
            time.sleep(random.uniform(3, 5))
            
            message_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//div[text()='Message']"))
            )
            message_button.click()
            time.sleep(random.uniform(2, 4))
            
            message_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//textarea[@placeholder='Message...']"))
            )
            message_input.send_keys(message)
            time.sleep(random.uniform(1, 2))
            
            send_button = self.driver.find_element(By.XPATH, "//button[text()='Send']")
            send_button.click()
            
            time.sleep(random.uniform(2, 4))
            print(f"Message sent to {username}")
            return True
            
        except Exception as e:
            print(f"Error sending message to {username}: {str(e)}")
            return False
    
    def run_campaign(self, campaign_id: int):
        """Run a campaign with safety limits"""
        try:
            campaign = Campaign.query.get(campaign_id)
            if not campaign or campaign.status != 'active':
                return
            
            today = datetime.now().date()
            messages_sent_today = Message.query.filter(
                Message.campaign_id == campaign_id,
                db.func.date(Message.sent_at) == today
            ).count()
            
            if messages_sent_today >= self.daily_message_limit:
                print(f"Daily limit reached for campaign {campaign_id}")
                return
            
            prospects = Prospect.query.filter(
                Prospect.status == ProspectStatus.QUALIFIED,
                Prospect.dm_sent == False
            ).limit(self.daily_message_limit - messages_sent_today).all()
            
            if not prospects:
                print("No qualified prospects to message")
                return
            
            self.setup_driver()
            if not self.login():
                return
            
            messages_sent = 0
            for prospect in prospects:
                if messages_sent >= (self.daily_message_limit - messages_sent_today):
                    break
                
                try:
                    prospect_data = {
                        'username': prospect.username,
                        'full_name': prospect.full_name,
                        'niche': prospect.niche,
                        'followers': prospect.followers
                    }
                    
                    message_content = MessageTemplates.get_personalized_message(prospect_data)
                    
                    if self.send_dm(prospect.username, message_content):
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
                        
                        delay = random.uniform(self.message_delay, self.message_delay * 1.5)
                        print(f"Waiting {delay:.1f} seconds before next message...")
                        time.sleep(delay)
                    
                except Exception as e:
                    print(f"Error messaging {prospect.username}: {str(e)}")
                    continue
            
            db.session.commit()
            print(f"Campaign completed. Sent {messages_sent} messages.")
            
        except Exception as e:
            print(f"Campaign error: {str(e)}")
            db.session.rollback()
        finally:
            if self.driver:
                self.driver.quit()
    
    def close(self):
        """Close the browser"""
        if self.driver:
            self.driver.quit()
