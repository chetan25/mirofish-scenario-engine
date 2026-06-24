"""
MiroFish Multi-Agent Scenario Engine
Agents debate and reason through complex decisions
"""

import os
import json
import requests
import asyncio
from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
from dotenv import load_dotenv

# Load environment from .env file
load_dotenv('/root/side-hustle-simulator/.env')
load_dotenv()

app = Flask(__name__)
CORS(app, resources={
    r"/*": {"origins": "*"}
}, allow_headers=['Content-Type', 'Authorization'])

OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')
print(f"✓ API Key loaded: {OPENROUTER_API_KEY[:20]}..." if OPENROUTER_API_KEY else "✗ API Key NOT found")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

# ===== AGENT DEFINITIONS =====
AGENTS = {
    # Side Hustle Agents
    'entrepreneur': {
        'name': 'Entrepreneur',
        'icon': '🚀',
        'role': 'Optimistic, ambitious. Sees the opportunity. Pushes boundaries.',
        'category': 'side_hustle'
    },
    'market': {
        'name': 'Market Analyst',
        'icon': '📊',
        'role': 'Realistic, data-driven. Analyzes market demand, competition, saturation.',
        'category': 'side_hustle'
    },
    'finance': {
        'name': 'Finance Advisor',
        'icon': '💰',
        'role': 'Pragmatic, risk-aware. Focuses on cash flow, runway, profitability.',
        'category': 'side_hustle'
    },
    'life': {
        'name': 'Life Coach',
        'icon': '⚖️',
        'role': 'Holistic, focused on wellbeing. Considers time, energy, relationships.',
        'category': 'side_hustle'
    },
    
    # Life Decision Agents
    'pragmatist': {
        'name': 'Pragmatist',
        'icon': '🎯',
        'role': 'Focus on practical outcomes, stability, risk minimization.',
        'category': 'life_decision'
    },
    'dreamer': {
        'name': 'Dreamer',
        'icon': '✨',
        'role': 'Focus on fulfillment, growth potential, life satisfaction.',
        'category': 'life_decision'
    },
    'analyst': {
        'name': 'Analyst',
        'icon': '🧠',
        'role': 'Deep dive into data, scenarios, probabilities, trade-offs.',
        'category': 'life_decision'
    },
    'advisor': {
        'name': 'Trusted Advisor',
        'icon': '🤝',
        'role': 'Consider relationships, social impact, long-term consequences.',
        'category': 'life_decision'
    }
}

# ===== QUESTIONNAIRES =====
QUESTIONNAIRES = {
    'side_hustle': [
        {
            'id': 'idea',
            'question': 'What is your side hustle idea?',
            'placeholder': 'E.g., freelance writing, SaaS product, consulting, etc.'
        },
        {
            'id': 'motivation',
            'question': 'Why are you considering this?',
            'placeholder': 'E.g., extra income, escape plan, passion project'
        },
        {
            'id': 'capital',
            'question': 'How much capital can you invest? ($)',
            'placeholder': '1000'
        },
        {
            'id': 'time',
            'question': 'How many hours per week can you commit?',
            'placeholder': '15'
        },
        {
            'id': 'skills',
            'question': 'What relevant skills/experience do you have?',
            'placeholder': 'E.g., 5 years marketing, built 3 products, etc.'
        },
        {
            'id': 'constraints',
            'question': 'Any constraints? (family, health, location, etc.)',
            'placeholder': 'E.g., no travel, must support family'
        },
        {
            'id': 'timeline',
            'question': 'What\'s your desired timeline to profitability?',
            'placeholder': '3-6 months'
        },
        {
            'id': 'goal',
            'question': 'End goal? (income replacement, side income, escape plan)',
            'placeholder': 'E.g., $5k/month in 1 year'
        }
    ],
    'life_decision': [
        {
            'id': 'decision',
            'question': 'What decision are you facing?',
            'placeholder': 'E.g., move cities, change careers, get married, go back to school'
        },
        {
            'id': 'options',
            'question': 'What are your options?',
            'placeholder': 'E.g., Option A: Stay and grow current role, Option B: New startup, Option C: Go freelance'
        },
        {
            'id': 'timeline',
            'question': 'Timeline: When must you decide?',
            'placeholder': '2 weeks, 3 months, etc.'
        },
        {
            'id': 'current_state',
            'question': 'Current situation (job, family, finances, happiness level)?',
            'placeholder': 'E.g., $100k/year, married, 2 kids, 60% happy'
        },
        {
            'id': 'motivations',
            'question': 'What\'s motivating this decision?',
            'placeholder': 'E.g., burnout, new opportunity, life stage change'
        },
        {
            'id': 'fears',
            'question': 'What are you afraid of?',
            'placeholder': 'E.g., losing income, failure, regret, disrupting family'
        },
        {
            'id': 'success',
            'question': 'How will you know if you made the right choice?',
            'placeholder': 'E.g., income maintained, happiness at 80%, family stable'
        },
        {
            'id': 'constraints',
            'question': 'Any hard constraints?',
            'placeholder': 'E.g., must support $X/month, can\'t relocate'
        }
    ]
}

# ===== CORE LOGIC =====

async def call_llm(prompt: str, temperature=0.7):
    """Call OpenRouter API"""
    try:
        response = requests.post(
            OPENROUTER_URL,
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "HTTP-Referer": "http://localhost:3000",
                "X-Title": "MiroFish",
                "Content-Type": "application/json"
            },
            json={
                "model": "anthropic/claude-3.5-sonnet",
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a structured analysis assistant. You MUST respond with ONLY the exact format below. No other text.\n\nFormat:\nKEY INSIGHT: [single sentence]\nPROS:\n- [point 1]\n- [point 2]\n- [point 3]\nCONS:\n- [risk 1]\n- [risk 2]\n- [risk 3]\nRECOMMENDATION: [verdict]"
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.2,
                "max_tokens": 200
            },
            timeout=30
        )
        
        if response.status_code != 200:
            return f"API Error {response.status_code}"
        
        data = response.json()
        return data['choices'][0]['message']['content'].strip()
    except Exception as e:
        print(f"[ERROR] LLM call failed: {e}")
        import traceback
        traceback.print_exc()
        return f"Error: {str(e)}"

async def agent_debate(scenario_type: str, context: dict, user_input: str = None):
    """Run multi-agent debate"""
    
    if scenario_type == 'side_hustle':
        agents_to_use = ['entrepreneur', 'market', 'finance', 'life']
        debate_topic = f"""
        Scenario: {context.get('idea', 'Side hustle opportunity')}
        
        Context:
        - Motivation: {context.get('motivation')}
        - Capital: ${context.get('capital')}
        - Time commitment: {context.get('time')} hrs/week
        - Skills: {context.get('skills')}
        - Constraints: {context.get('constraints')}
        - Timeline goal: {context.get('timeline')}
        - End goal: {context.get('goal')}
        """
    else:  # life_decision
        agents_to_use = ['pragmatist', 'dreamer', 'analyst', 'advisor']
        debate_topic = f"""
        Decision: {context.get('decision')}
        
        Options:
        {context.get('options')}
        
        Context:
        - Current state: {context.get('current_state')}
        - Motivations: {context.get('motivations')}
        - Fears: {context.get('fears')}
        - Success criteria: {context.get('success')}
        - Hard constraints: {context.get('constraints')}
        - Timeline: {context.get('timeline')}
        """
    
    if user_input:
        debate_topic += f"\n\nNew information: {user_input}"
    
    results = []
    
    for agent_key in agents_to_use:
        agent = AGENTS[agent_key]
        
        prompt = f"""
You are {agent['name']} ({agent['role']})

{debate_topic}

RESPOND ONLY IN THIS EXACT FORMAT - NO OTHER TEXT:

KEY INSIGHT: [One powerful insight in 1 sentence]

PROS:
- [Positive factor 1]
- [Positive factor 2]
- [Positive factor 3]

CONS:
- [Risk or concern 1]
- [Risk or concern 2]
- [Risk or concern 3]

RECOMMENDATION: [Your 1-sentence verdict: GO, NO-GO, or PROCEED WITH CAUTION]

Do not include anything else. No explanations, no preamble.
"""
        
        perspective = await call_llm(prompt, temperature=0.3)  # Lower temp for stricter format adherence
        
        results.append({
            'agent': agent['name'],
            'icon': agent['icon'],
            'perspective': perspective,
            'timestamp': datetime.now().isoformat()
        })
    
    return results

async def synthesize_consensus(scenario_type: str, context: dict, debate_results: list):
    """Synthesize agent debate into consensus"""
    
    # Extract key points from debate
    perspectives_summary = "\n\n".join([
        f"{r['agent']}: {r['perspective'][:200]}..."
        for r in debate_results
    ])
    
    prompt = f"""Based on these 4 agent perspectives on this scenario:

{perspectives_summary}

Give a brief consensus analysis (3-4 sentences max):
1. What's the likely outcome?
2. What's the key risk?
3. What's the main opportunity?
4. Overall: Confidence level (0-100%)

Be concise and direct."""
    
    consensus = await call_llm(prompt, temperature=0.5)
    return consensus

# ===== API ENDPOINTS =====

@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'ok',
        'service': 'MiroFish Multi-Agent Scenario Engine',
        'agents': len(AGENTS),
        'timestamp': datetime.now().isoformat()
    })

@app.route('/questionnaire/<scenario_type>', methods=['GET'])
def get_questionnaire(scenario_type):
    """Get questionnaire for scenario type"""
    if scenario_type not in QUESTIONNAIRES:
        return jsonify({'error': 'Invalid scenario type'}), 400
    
    return jsonify({
        'scenario_type': scenario_type,
        'questions': QUESTIONNAIRES[scenario_type]
    })

@app.route('/agents/<scenario_type>', methods=['GET'])
def get_agents(scenario_type):
    """Get agents for scenario type"""
    scenario_agents = [
        {'key': k, **v}
        for k, v in AGENTS.items()
        if v['category'] == scenario_type
    ]
    
    return jsonify({'agents': scenario_agents})

@app.route('/debate', methods=['POST'])
def start_debate():
    """Start multi-agent debate"""
    try:
        data = request.json
        scenario_type = data.get('scenario_type')
        context = data.get('context', {})
        user_input = data.get('user_input')
        
        if not scenario_type:
            return jsonify({'error': 'scenario_type required'}), 400
        
        # Run async function
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        debate_results = loop.run_until_complete(agent_debate(scenario_type, context, user_input))
        consensus = loop.run_until_complete(synthesize_consensus(scenario_type, context, debate_results))
        
        loop.close()
        
        return jsonify({
            'scenario_type': scenario_type,
            'debate': debate_results,
            'consensus': consensus,
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        print(f"Error in /debate: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/debate/continue', methods=['POST'])
def continue_debate():
    """Continue debate with user input"""
    try:
        data = request.json
        scenario_type = data.get('scenario_type')
        context = data.get('context', {})
        user_input = data.get('user_input')
        previous_debate = data.get('previous_debate', [])
        
        if not user_input:
            return jsonify({'error': 'user_input required'}), 400
        
        # Run async function
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        debate_results = loop.run_until_complete(agent_debate(scenario_type, context, user_input))
        combined = previous_debate + debate_results
        consensus = loop.run_until_complete(synthesize_consensus(scenario_type, context, combined))
        
        loop.close()
        
        return jsonify({
            'scenario_type': scenario_type,
            'new_debate': debate_results,
            'all_debate': combined,
            'consensus': consensus,
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        print(f"Error in /debate/continue: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("""
╔════════════════════════════════════════════════════════════╗
║   MiroFish Multi-Agent Scenario Engine                     ║
║   Powered by OpenRouter + Agent Debate                     ║
╚════════════════════════════════════════════════════════════╝

✓ Agents: 8 (4 for Side Hustle, 4 for Life Decisions)
✓ Questionnaires: 2 (contextual, adaptive)
✓ Features: Live debate, user input, consensus synthesis

🚀 Starting on http://0.0.0.0:5001
""")
    
    app.run(host='0.0.0.0', port=5001, debug=False)
