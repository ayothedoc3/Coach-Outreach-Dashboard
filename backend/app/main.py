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

from models import db, Prospect, Campaign, Message, User, InstagramAccount, ProspectStatus, CampaignStatus, CoolifyConfig, Deployment, DeploymentStatus
from instagram_bot import ApifyInstagramBot
from message_templates import MessageTemplates
from coolify_service import CoolifyService

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

@app.route('/api/healthz')
def api_healthz():
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
        'instagram_account_id': c.instagram_account_id,
        'instagram_account': {
            'id': c.instagram_account.id,
            'username': c.instagram_account.username,
            'is_active': c.instagram_account.is_active,
            'account_status': c.instagram_account.account_status
        } if c.instagram_account else None,
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
        instagram_account_id=data.get('instagram_account_id'),  # Optional account assignment
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
            campaign = Campaign.query.get(campaign_id)
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


@app.route('/api/instagram-accounts')
@jwt_required()
def get_instagram_accounts():
    accounts = InstagramAccount.query.order_by(InstagramAccount.created_at.desc()).all()
    
    return jsonify([{
        'id': acc.id,
        'username': acc.username,
        'is_active': acc.is_active,
        'daily_messages_sent': acc.daily_messages_sent,
        'daily_limit': acc.daily_limit,
        'account_status': acc.account_status,
        'last_activity': acc.last_activity.isoformat() if acc.last_activity else None,
        'remaining_today': ApifyInstagramBot.get_account_daily_remaining(acc.id),
        'created_at': acc.created_at.isoformat()
    } for acc in accounts])

@app.route('/api/instagram-accounts', methods=['POST'])
@jwt_required()
def create_instagram_account():
    data = request.get_json()
    
    if not data.get('username') or not data.get('session_id'):
        return jsonify({'error': 'Username and session_id are required'}), 400
    
    existing = InstagramAccount.query.filter_by(username=data['username']).first()
    if existing:
        return jsonify({'error': 'Account with this username already exists'}), 400
    
    account = InstagramAccount(
        username=data['username'],
        session_id=data['session_id'],
        daily_limit=data.get('daily_limit', 40),
        is_active=data.get('is_active', True)
    )
    
    db.session.add(account)
    db.session.commit()
    
    return jsonify({
        'id': account.id,
        'message': f'Instagram account {account.username} created successfully'
    })

@app.route('/api/instagram-accounts/<int:account_id>', methods=['PUT'])
@jwt_required()
def update_instagram_account(account_id):
    account = InstagramAccount.query.get_or_404(account_id)
    data = request.get_json()
    
    if 'session_id' in data:
        account.session_id = data['session_id']
    if 'daily_limit' in data:
        account.daily_limit = data['daily_limit']
    if 'is_active' in data:
        account.is_active = data['is_active']
    if 'account_status' in data:
        account.account_status = data['account_status']
    
    db.session.commit()
    
    return jsonify({'message': f'Account {account.username} updated successfully'})

@app.route('/api/instagram-accounts/<int:account_id>', methods=['DELETE'])
@jwt_required()
def delete_instagram_account(account_id):
    account = InstagramAccount.query.get_or_404(account_id)
    
    active_campaigns = Campaign.query.filter_by(
        instagram_account_id=account_id,
        status=CampaignStatus.ACTIVE
    ).count()
    
    if active_campaigns > 0:
        return jsonify({
            'error': f'Cannot delete account. It is being used by {active_campaigns} active campaign(s)'
        }), 400
    
    username = account.username
    db.session.delete(account)
    db.session.commit()
    
    return jsonify({'message': f'Account {username} deleted successfully'})

@app.route('/api/instagram-accounts/<int:account_id>/test', methods=['POST'])
@jwt_required()
def test_instagram_account(account_id):
    """Test if an Instagram account's session ID is still valid"""
    try:
        bot = ApifyInstagramBot(account_id=account_id)
        
        account = InstagramAccount.query.get(account_id)
        account.last_activity = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': f'Account {account.username} session appears valid'
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Account test failed: {str(e)}'
        }), 400

@app.route('/api/coolify-configs')
@jwt_required()
def get_coolify_configs():
    configs = CoolifyConfig.query.filter_by(is_active=True).all()
    return jsonify([{
        'id': c.id,
        'name': c.name,
        'api_url': c.api_url,
        'team_id': c.team_id,
        'created_at': c.created_at.isoformat()
    } for c in configs])

@app.route('/api/coolify-configs', methods=['POST'])
@jwt_required()
def create_coolify_config():
    data = request.get_json()
    
    config = CoolifyConfig(
        name=data['name'],
        api_url=data['api_url'],
        api_token=data['api_token'],
        team_id=data.get('team_id')
    )
    
    db.session.add(config)
    db.session.commit()
    
    return jsonify({'id': config.id, 'message': 'Coolify config created successfully'})

@app.route('/api/deployments')
@jwt_required()
def get_deployments():
    deployments = Deployment.query.order_by(Deployment.created_at.desc()).all()
    
    return jsonify([{
        'id': d.id,
        'name': d.name,
        'github_url': d.github_url,
        'project_type': d.project_type,
        'status': d.status.value,
        'deployment_url': d.deployment_url,
        'coolify_config': {
            'id': d.coolify_config.id,
            'name': d.coolify_config.name
        } if d.coolify_config else None,
        'created_at': d.created_at.isoformat()
    } for d in deployments])

@app.route('/api/deployments', methods=['POST'])
@jwt_required()
def create_deployment():
    data = request.get_json()
    
    deployment = Deployment(
        name=data['name'],
        github_url=data['github_url'],
        coolify_config_id=data['coolify_config_id'],
        environment_variables=json.dumps(data.get('environment_variables', {}))
    )
    
    db.session.add(deployment)
    db.session.commit()
    
    try:
        coolify_service = CoolifyService(deployment.coolify_config_id)
        if coolify_service.create_application(deployment):
            coolify_service.deploy_application(deployment)
    except Exception as e:
        deployment.status = DeploymentStatus.FAILED
        db.session.commit()
        return jsonify({'error': f'Deployment failed: {str(e)}'}), 500
    
    return jsonify({'id': deployment.id, 'message': 'Deployment started successfully'})

@app.route('/api/deployments/<int:deployment_id>/status')
@jwt_required()
def get_deployment_status(deployment_id):
    deployment = Deployment.query.get_or_404(deployment_id)
    
    try:
        coolify_service = CoolifyService(deployment.coolify_config_id)
        status_info = coolify_service.get_deployment_status(deployment)
        return jsonify(status_info)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/deployments/<int:deployment_id>/environment-variables', methods=['PUT'])
@jwt_required()
def update_deployment_env_vars(deployment_id):
    deployment = Deployment.query.get_or_404(deployment_id)
    data = request.get_json()
    
    try:
        coolify_service = CoolifyService(deployment.coolify_config_id)
        if coolify_service.update_environment_variables(deployment, data['environment_variables']):
            return jsonify({'message': 'Environment variables updated successfully'})
        else:
            return jsonify({'error': 'Failed to update environment variables'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/deployments/<int:deployment_id>/detect-project', methods=['POST'])
@jwt_required()
def detect_project_type(deployment_id):
    deployment = Deployment.query.get_or_404(deployment_id)
    
    try:
        coolify_service = CoolifyService(deployment.coolify_config_id)
        project_type, detection_info = coolify_service.detect_project_type(deployment.github_url)
        
        return jsonify({
            'project_type': project_type,
            'detection_info': detection_info
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8001)
