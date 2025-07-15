import random
from typing import Dict, List

class MessageTemplates:
    
    BUSINESS_COACH_TEMPLATES = [
        "Hi {name}! Love your business coaching content. We help coaches like you scale to 6-figures with done-for-you funnels and landing pages. Would you be interested in learning how we've helped coaches increase their revenue by 300%?",
        "Hey {name}! Your {niche} expertise is impressive. We specialize in building high-converting sales funnels for coaches. Our clients typically see 2-5x revenue growth. Mind if I share how we could help scale your coaching business?",
        "Hi {name}! Noticed you're helping entrepreneurs succeed - that's awesome! We build custom landing pages and hire closers for coaches, taking a % of increased revenue. Would love to show you our case studies. Interested?",
        "Hey {name}! Your business coaching content resonates with so many people. We help coaches like you automate their sales process with proven funnels. Our average client sees $50K+ monthly increases. Can I share more?",
        "Hi {name}! Love what you're doing in the business coaching space. We partner with coaches to build their sales infrastructure - funnels, pages, closers - and only get paid when you make more money. Worth a quick chat?"
    ]
    
    LIFE_COACH_TEMPLATES = [
        "Hi {name}! Your life coaching content is truly inspiring. We help coaches scale their impact with professional funnels and landing pages. Our clients typically 3x their coaching revenue. Would you be open to learning more?",
        "Hey {name}! Love how you're transforming lives through coaching. We specialize in building high-converting sales systems for life coaches. Mind if I share how we've helped coaches reach 6-figure months?",
        "Hi {name}! Your approach to {niche} coaching is amazing. We build done-for-you sales funnels and provide closers for coaches, taking only a % of increased revenue. Interested in seeing our results?",
        "Hey {name}! Noticed you're making a real difference in people's lives. We help life coaches scale their business with proven marketing systems. Our average client sees 200%+ revenue growth. Worth exploring?",
        "Hi {name}! Your life coaching expertise shines through your content. We partner with coaches to build their entire sales infrastructure. Only pay us when you make more money. Can I show you how?"
    ]
    
    FITNESS_COACH_TEMPLATES = [
        "Hi {name}! Your fitness coaching content is motivating! We help fitness coaches scale with high-converting funnels and landing pages. Our clients typically see 250%+ revenue increases. Would you be interested in learning more?",
        "Hey {name}! Love your approach to fitness coaching. We build custom sales systems for coaches and provide professional closers. Our average client reaches $30K+ monthly. Mind if I share our case studies?",
        "Hi {name}! Your fitness expertise is impressive. We specialize in scaling coaching businesses with done-for-you marketing systems. Only get paid when you make more money. Worth a conversation?",
        "Hey {name}! Noticed you're helping people transform their health - amazing work! We build sales funnels and hire closers for fitness coaches. Our clients typically 3x their revenue. Interested?",
        "Hi {name}! Your fitness coaching content stands out. We partner with coaches to build their entire sales infrastructure - funnels, pages, closers. Performance-based pricing. Can I show you our results?"
    ]
    
    MINDSET_COACH_TEMPLATES = [
        "Hi {name}! Your mindset coaching content is powerful. We help coaches like you scale with professional sales funnels and landing pages. Our clients typically see 300%+ revenue growth. Would you be open to learning more?",
        "Hey {name}! Love how you're helping people transform their mindset. We build high-converting sales systems for coaches and provide closers. Mind if I share how we've helped coaches reach 6-figures?",
        "Hi {name}! Your approach to mindset coaching is inspiring. We specialize in scaling coaching businesses with done-for-you marketing infrastructure. Only pay when you make more. Worth exploring?",
        "Hey {name}! Noticed you're making a real impact on people's mindset. We build custom funnels and hire professional closers for coaches. Our average client sees 250%+ increases. Interested?",
        "Hi {name}! Your mindset expertise shines through your content. We partner with coaches to build their complete sales system. Performance-based model - you only pay when revenue increases. Can I share more?"
    ]
    
    FOLLOW_UP_TEMPLATES = [
        "Hi {name}! Following up on my previous message about scaling your coaching business. We've just helped another coach in your niche reach $75K/month. Would love to share the strategy with you!",
        "Hey {name}! Hope you're doing well! Still interested in learning how we help coaches 3x their revenue with done-for-you funnels? Happy to share some quick case studies.",
        "Hi {name}! Wanted to circle back - we just launched a new program specifically for {niche} coaches. Our latest client went from $10K to $45K monthly in 90 days. Worth a quick chat?",
        "Hey {name}! Following up on scaling your coaching business. We're currently working with 3 coaches in your space who are seeing incredible results. Mind if I share what's working?",
        "Hi {name}! Hope you saw my previous message about our coaching business scaling system. We have a limited-time case study I'd love to share with you. Interested?"
    ]
    
    @classmethod
    def get_template(cls, niche: str, message_type: str = 'initial') -> str:
        """Get a random template based on niche and message type"""
        
        if message_type == 'follow_up':
            return random.choice(cls.FOLLOW_UP_TEMPLATES)
        
        niche_lower = niche.lower() if niche else 'business'
        
        if 'business' in niche_lower or 'entrepreneur' in niche_lower:
            templates = cls.BUSINESS_COACH_TEMPLATES
        elif 'life' in niche_lower or 'personal' in niche_lower:
            templates = cls.LIFE_COACH_TEMPLATES
        elif 'fitness' in niche_lower or 'health' in niche_lower or 'wellness' in niche_lower:
            templates = cls.FITNESS_COACH_TEMPLATES
        elif 'mindset' in niche_lower or 'mental' in niche_lower or 'psychology' in niche_lower:
            templates = cls.MINDSET_COACH_TEMPLATES
        else:
            templates = cls.BUSINESS_COACH_TEMPLATES  # Default fallback
            
        return random.choice(templates)
    
    @classmethod
    def personalize_message(cls, template: str, prospect_data: Dict) -> str:
        """Personalize a template with prospect data"""
        
        name = prospect_data.get('full_name', '').split()[0] if prospect_data.get('full_name') else prospect_data.get('username', 'there')
        niche = prospect_data.get('niche', 'coaching')
        
        if not name or name == 'there':
            name = prospect_data.get('username', 'there')
        
        return template.format(
            name=name,
            niche=niche,
            username=prospect_data.get('username', ''),
            followers=prospect_data.get('followers', 0)
        )
    
    @classmethod
    def get_personalized_message(cls, prospect_data: Dict, message_type: str = 'initial') -> str:
        """Get a personalized message for a prospect"""
        
        niche = prospect_data.get('niche', 'business')
        template = cls.get_template(niche, message_type)
        return cls.personalize_message(template, prospect_data)
