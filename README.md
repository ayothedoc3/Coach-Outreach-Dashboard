# Coach Outreach Dashboard

A complete Instagram coach outreach automation system with professional dashboard for finding, qualifying, and messaging coaches with 10K+ followers.

## 🎯 Overview

This system automates Instagram outreach to coaches selling $1K+ programs, providing:
- **Prospect Discovery**: Scrape Instagram hashtags and competitor followers
- **AI-Powered Qualification**: OpenAI integration for bio analysis and scoring
- **Automated Messaging**: Safe DM sending with rate limiting (50/day max)
- **Campaign Management**: Multi-campaign support with analytics
- **Professional Dashboard**: Real-time metrics and performance tracking

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- Node.js 18+
- Docker & Docker Compose (optional)

### Local Development

1. **Clone and Setup**
```bash
git clone <repository-url>
cd coach-outreach-dashboard
cp .env.example .env
# Edit .env with your credentials
```

2. **Backend Setup**
```bash
cd backend
poetry install
poetry run python app/main.py
# Backend runs on http://localhost:8001
```

3. **Frontend Setup**
```bash
cd frontend
npm install
npm run dev
# Frontend runs on http://localhost:5174
```

4. **Access Dashboard**
- Open http://localhost:5174
- Login with demo credentials: `admin` / `admin`

### Docker Deployment

```bash
docker-compose up -d
```
- Frontend: http://localhost:3000
- Backend: http://localhost:8000

## 📁 Project Structure

```
coach-outreach-dashboard/
├── backend/                 # Flask API + InstaPy automation
│   ├── app/
│   │   └── main.py         # Main Flask application
│   ├── models.py           # Database models
│   ├── instagram_bot.py    # InstaPy automation logic
│   ├── message_templates.py # Personalized DM templates
│   ├── pyproject.toml      # Python dependencies
│   └── Dockerfile          # Backend container
├── frontend/               # React dashboard
│   ├── src/
│   │   ├── components/     # Dashboard components
│   │   ├── contexts/       # Authentication context
│   │   └── App.tsx         # Main application
│   ├── package.json        # Frontend dependencies
│   ├── tailwind.config.js  # Tailwind CSS config
│   └── Dockerfile          # Frontend container
├── data/                   # Database and logs
├── docker-compose.yml      # Full stack deployment
├── .env.example           # Environment template
└── README.md              # This file
```

## 🔧 Features

### Backend (Flask + InstaPy)
- **Authentication**: JWT-based login system
- **Database**: SQLite with prospect/campaign tracking
- **InstaPy Integration**: Automated Instagram interactions
- **API Endpoints**: RESTful API for dashboard
- **Safety Features**: Rate limiting, proxy support, account protection

### Frontend (React Dashboard)
- **Modern UI**: Clean, professional interface with Tailwind CSS
- **Real-time Data**: Live campaign metrics and prospect management
- **Interactive Charts**: Performance tracking with Recharts
- **Responsive Design**: Works on desktop and mobile
- **User Management**: Role-based access control

### Core Functionality

#### 1. Prospect Discovery Engine
- Scrape Instagram hashtags: #businesscoach, #lifecoach, etc.
- Analyze competitor followers
- Filter by follower count (10K-100K)
- Bio analysis for coaching keywords
- Engagement rate calculation

#### 2. AI-Powered Qualification
- OpenAI integration for bio analysis
- Score prospects (coach score + value score)
- Identify high-value indicators ($1K+, "premium", "exclusive")
- Niche classification (business, fitness, mindset, etc.)

#### 3. Automated Messaging System
- Personalized DM templates by niche
- Safe sending limits (50/day max)
- Follow-up sequences
- Response tracking
- Account rotation support

#### 4. Campaign Management
- Multiple campaign support
- Hashtag and account targeting
- Performance analytics
- Start/stop controls
- Daily/weekly reporting

#### 5. Dashboard Analytics
- Real-time metrics display
- Conversion funnel tracking
- Response rate analysis
- ROI calculations
- Export capabilities

## 🔒 Safety & Compliance

### Account Protection
- Conservative rate limits (50 DMs/day max)
- Random delays between actions (2-3 minutes)
- Proxy rotation support
- Account warming protocols
- Emergency stop mechanisms

### Anti-Detection Measures
- Human-like behavior patterns
- User agent rotation
- Session management
- Activity logging
- Error handling

## 📊 Dashboard Components

### Overview Tab
- Key metrics cards (prospects, messages, responses, conversions)
- Daily performance chart (messages vs responses)
- Niche distribution pie chart
- Campaign status indicators
- Daily limit progress bars

### Prospects Tab
- Searchable prospect table
- Filtering by status, niche, scores
- Bulk actions (send message, mark converted)
- Prospect detail modals
- Export to CSV

### Campaigns Tab
- Campaign creation wizard
- Active/paused campaign cards
- Performance metrics per campaign
- Target configuration (hashtags, accounts)
- Message template management

### Analytics Tab
- Advanced reporting dashboard
- Time-series performance charts
- Conversion funnel analysis
- A/B testing results
- ROI calculations

## ⚙️ Configuration

### Environment Variables (.env)

```env
# Instagram Credentials
INSTAGRAM_USERNAME=your_username
INSTAGRAM_PASSWORD=your_password

# API Configuration
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret

# OpenAI Integration
OPENAI_API_KEY=your-openai-key

# Automation Settings
DAILY_MESSAGE_LIMIT=50
MESSAGE_DELAY=120
HEADLESS=true

# Database
DATABASE_URL=sqlite:///coach_outreach.db

# Flask Configuration
FLASK_ENV=development
```

### Message Templates

The system includes personalized templates like:
- "Hi {name}! Love your {niche} content. We help coaches scale to 6-figures with done-for-you funnels..."
- 5+ variations per message type
- Niche-specific customization
- Call-to-action focused

## 🗄️ Database Schema

```sql
-- Prospects table
CREATE TABLE prospects (
    id INTEGER PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    followers INTEGER,
    engagement_rate FLOAT,
    bio TEXT,
    coach_score FLOAT,
    value_score FLOAT,
    niche VARCHAR(20),
    status VARCHAR(20),
    dm_sent BOOLEAN DEFAULT FALSE,
    response_received BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Campaigns table
CREATE TABLE campaigns (
    id INTEGER PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    hashtags TEXT,
    target_accounts TEXT,
    daily_limit INTEGER DEFAULT 50,
    status VARCHAR(20) DEFAULT 'paused',
    messages_sent INTEGER DEFAULT 0,
    responses INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Messages table
CREATE TABLE messages (
    id INTEGER PRIMARY KEY,
    prospect_id INTEGER,
    campaign_id INTEGER,
    content TEXT,
    sent_at TIMESTAMP,
    response_at TIMESTAMP,
    FOREIGN KEY (prospect_id) REFERENCES prospects (id),
    FOREIGN KEY (campaign_id) REFERENCES campaigns (id)
);
```

## 🚀 API Endpoints

### Authentication
- `POST /api/auth/login` - User login
- `GET /healthz` - Health check

### Dashboard
- `GET /api/dashboard/stats` - Dashboard statistics
- `GET /api/prospects` - Get prospects with filtering
- `GET /api/campaigns` - Get campaigns
- `POST /api/campaigns` - Create campaign
- `POST /api/campaigns/{id}/start` - Start campaign
- `POST /api/campaigns/{id}/pause` - Pause campaign

### Automation
- `POST /api/scrape/hashtag` - Scrape hashtag for prospects
- `POST /api/prospects/{id}/message` - Send message to prospect
- `GET /api/analytics/performance` - Performance analytics

## 📈 Success Metrics

The system is designed to achieve:
- 100-200 qualified prospects identified daily
- 50 personalized messages sent safely
- 5-15% response rate
- 2-7 qualified leads per day
- Zero account suspensions

## 🛠️ Development

### Backend Development
```bash
cd backend
poetry install
poetry run python app/main.py
```

### Frontend Development
```bash
cd frontend
npm install
npm run dev
```

### Testing
```bash
# Backend tests
cd backend
poetry run pytest

# Frontend tests
cd frontend
npm test
```

## 🐳 Docker Deployment

### Build and Run
```bash
docker-compose up --build -d
```

### View Logs
```bash
docker-compose logs -f
```

### Stop Services
```bash
docker-compose down
```

## 🔧 Troubleshooting

### Common Issues

1. **Port Already in Use**
   ```bash
   # Kill process on port
   lsof -ti:8001 | xargs kill -9
   ```

2. **Instagram Login Issues**
   - Check credentials in .env
   - Enable 2FA and use app password
   - Use proxy if IP blocked

3. **Frontend Not Loading**
   ```bash
   cd frontend
   rm -rf node_modules
   npm install
   npm run dev
   ```

4. **Database Issues**
   ```bash
   # Reset database
   rm data/coach_outreach.db
   # Restart backend to recreate
   ```

## 📝 License

This project is for educational and business use. Please comply with Instagram's Terms of Service and use responsibly.

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Make changes
4. Test thoroughly
5. Submit pull request

## 📞 Support

For issues and questions:
- Check troubleshooting section
- Review logs in `data/` directory
- Ensure all environment variables are set
- Test with demo credentials first

---

**⚠️ Important**: Always use this system responsibly and in compliance with Instagram's Terms of Service. Start with small limits and gradually increase as you verify account safety.
