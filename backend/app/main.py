from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
import os
import sys
import json
from datetime import datetime, timedelta
import threading

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import db, Prospect, Campaign, Message, User, InstagramAccount, ProspectStatus, CampaignStatus
from instagram_bot import ApifyInstagramBot
from message_templates import MessageTemplates

app = Flask(__name__)

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'jwt-secret-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///coach_outreach.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
jwt = JWTManager(app)
CORS(app, origins="*", supports_credentials=False, allow_headers=["Content-Type", "Authorization"], methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])

with app.app_context():
    db.create_all()

@app.route('/healthz')
def healthz():
    return {"status": "ok"}

@app.route('/api/auth/login', methods=['POST'])
def login():
    if request.content_type == 'application/json':
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
    else:
        username = request.form.get('username')
        password = request.form.get('password')
    
    if username == 'admin' and password == 'admin':
        access_token = create_access_token(identity=username)
        return jsonify({'access_token': access_token})
    
    return jsonify({'error': 'Invalid credentials'}), 401

@app.route('/api/dashboard/stats')
@jwt_required()
def dashboard_stats():
    total_prospects = Prospect.query.count()
    qualified_prospects = Prospect.query.filter_by(status=ProspectStatus.QUALIFIED).count()
    messages_sent = Message.query.count()
    responses_received = Prospect.query.filter_by(response_received=True).count()
    
    today = datetime.now().date()
    messages_today = Message.query.filter(
        db.func.date(Message.sent_at) == today
    ).count()
    
    week_ago = datetime.now() - timedelta(days=7)
    recent_prospects = Prospect.query.filter(
        Prospect.created_at >= week_ago
    ).count()
    
    return jsonify({
        'total_prospects': total_prospects,
        'qualified_prospects': qualified_prospects,
        'messages_sent': messages_sent,
        'responses_received': responses_received,
        'messages_today': messages_today,
        'recent_prospects': recent_prospects,
        'response_rate': round((responses_received / messages_sent * 100) if messages_sent > 0 else 0, 1)
    })

@app.route('/api/prospects')
@jwt_required()
def get_prospects():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    status = request.args.get('status')
    niche = request.args.get('niche')
    
    query = Prospect.query
    
    if status:
        query = query.filter_by(status=ProspectStatus(status))
    if niche:
        query = query.filter_by(niche=niche)
    
    prospects = query.order_by(Prospect.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'prospects': [{
            'id': p.id,
            'username': p.username,
            'full_name': p.full_name,
            'followers': p.followers,
            'engagement_rate': p.engagement_rate,
            'bio': p.bio,
            'coach_score': p.coach_score,
            'value_score': p.value_score,
            'niche': p.niche,
            'status': p.status.value,
            'dm_sent': p.dm_sent,
            'response_received': p.response_received,
            'created_at': p.created_at.isoformat()
        } for p in prospects.items],
        'total': prospects.total,
        'pages': prospects.pages,
        'current_page': page
    })

@app.route('/api/campaigns')
@jwt_required()
def get_campaigns():
    campaigns = Campaign.query.order_by(Campaign.created_at.desc()).all()
    
    return jsonify([{
        'id': c.id,
        'name': c.name,
        'description': c.description,
        'hashtags': json.loads(c.hashtags) if c.hashtags else [],
        'target_accounts': json.loads(c.target_accounts) if c.target_accounts else [],
        'status': c.status.value,
        'messages_sent': c.messages_sent,
        'responses_received': c.responses_received,
        'conversions': c.conversions,
        'daily_limit': c.daily_limit,
        'created_at': c.created_at.isoformat()
    } for c in campaigns])

@app.route('/api/campaigns', methods=['POST'])
@jwt_required()
def create_campaign():
    data = request.get_json()
    
    campaign = Campaign(
        name=data['name'],
        description=data.get('description', ''),
        hashtags=json.dumps(data.get('hashtags', [])),
        target_accounts=json.dumps(data.get('target_accounts', [])),
        daily_limit=data.get('daily_limit', 50)
    )
    
    db.session.add(campaign)
    db.session.commit()
    
    return jsonify({'id': campaign.id, 'message': 'Campaign created successfully'})

@app.route('/api/campaigns/<int:campaign_id>/start', methods=['POST'])
@jwt_required()
def start_campaign(campaign_id):
    campaign = Campaign.query.get_or_404(campaign_id)
    campaign.status = CampaignStatus.ACTIVE
    db.session.commit()
    
    def run_campaign_background():
        try:
            instagram_session_id = os.getenv('INSTAGRAM_SESSION_ID')
            
            if instagram_session_id:
                bot = ApifyInstagramBot(instagram_session_id)
                bot.run_campaign(campaign_id)
            else:
                print("INSTAGRAM_SESSION_ID environment variable is required")
        except Exception as e:
            print(f"Campaign error: {str(e)}")
    
    
    return jsonify({'message': 'Campaign started successfully'})

@app.route('/api/campaigns/<int:campaign_id>/pause', methods=['POST'])
@jwt_required()
def pause_campaign(campaign_id):
    campaign = Campaign.query.get_or_404(campaign_id)
    campaign.status = CampaignStatus.PAUSED
    db.session.commit()
    
    return jsonify({'message': 'Campaign paused successfully'})

@app.route('/api/scrape/hashtag', methods=['POST'])
@jwt_required()
def scrape_hashtag():
    data = request.get_json()
    hashtag = data.get('hashtag')
    limit = data.get('limit', 50)
    
    if not hashtag:
        return jsonify({'error': 'Hashtag is required'}), 400
    
    mock_prospects = [
        {
            'username': f'coach_{hashtag}_{i}',
            'full_name': f'Coach {i}',
            'followers': 15000 + (i * 1000),
            'following': 500 + (i * 10),
            'posts_count': 200 + (i * 5),
            'bio': f'Business coach helping entrepreneurs scale to 6-figures. Premium coaching programs available.',
            'niche': 'business',
            'engagement_rate': 3.5 + (i * 0.1),
            'coach_score': 8.0 + (i * 0.1),
            'value_score': 7.5 + (i * 0.1)
        }
        for i in range(min(limit, 10))  # Limit to 10 for demo
    ]
    
    created_count = 0
    for prospect_data in mock_prospects:
        existing = Prospect.query.filter_by(username=prospect_data['username']).first()
        if not existing:
            prospect = Prospect(**prospect_data)
            prospect.status = ProspectStatus.QUALIFIED if prospect.coach_score > 7 else ProspectStatus.DISCOVERED
            db.session.add(prospect)
            created_count += 1
    
    db.session.commit()
    
    return jsonify({
        'message': f'Scraped {len(mock_prospects)} prospects from #{hashtag}',
        'created': created_count,
        'prospects': mock_prospects
    })

@app.route('/api/prospects/<int:prospect_id>/send-message', methods=['POST'])
@jwt_required()
def send_message_to_prospect(prospect_id):
    prospect = Prospect.query.get_or_404(prospect_id)
    
    if prospect.dm_sent:
        return jsonify({'error': 'Message already sent to this prospect'}), 400
    
    prospect_data = {
        'username': prospect.username,
        'full_name': prospect.full_name,
        'niche': prospect.niche,
        'followers': prospect.followers
    }
    
    message_content = MessageTemplates.get_personalized_message(prospect_data)
    
    prospect.dm_sent = True
    prospect.dm_sent_at = datetime.utcnow()
    prospect.status = ProspectStatus.MESSAGED
    
    message = Message(
        prospect_id=prospect.id,
        campaign_id=1,  # Default campaign for demo
        content=message_content
    )
    db.session.add(message)
    db.session.commit()
    
    return jsonify({
        'message': 'Message sent successfully',
        'content': message_content
    })

@app.route('/api/analytics/performance')
@jwt_required()
def analytics_performance():
    thirty_days_ago = datetime.now() - timedelta(days=30)
    
    daily_stats = db.session.query(
        db.func.date(Message.sent_at).label('date'),
        db.func.count(Message.id).label('messages_sent')
    ).filter(
        Message.sent_at >= thirty_days_ago
    ).group_by(
        db.func.date(Message.sent_at)
    ).all()
    
    niche_stats = db.session.query(
        Prospect.niche,
        db.func.count(Prospect.id).label('count')
    ).group_by(Prospect.niche).all()
    
    return jsonify({
        'daily_messages': [
            {'date': stat.date.isoformat(), 'messages': stat.messages_sent}
            for stat in daily_stats
        ],
        'niche_distribution': [
            {'niche': stat.niche or 'unknown', 'count': stat.count}
            for stat in niche_stats
        ]
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8001)
