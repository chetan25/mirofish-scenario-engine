# MiroFish Multi-Agent Scenario Engine

AI-powered multi-agent reasoning system for exploring complex decisions through structured debate and consensus.

## Overview

MiroFish Scenario Engine enables genuine multi-agent reasoning where 4 independent agents debate any scenario from different perspectives, then reach consensus. Perfect for exploring side hustles, life decisions, business strategies, or any complex choice.

## Features

### 🤖 Multi-Agent Debates
- **4 independent agents** with distinct perspectives
- **Real LLM reasoning** - each agent thinks independently
- **Structured output** - Pros, Cons, Recommendations
- **User interjection** - add context mid-debate to change reasoning
- **Live visualization** - watch agents analyze in real-time

### 📋 Two Scenario Types
1. **Side Hustle** (Business Ideas)
   - Entrepreneur, Market Analyst, Finance Advisor, Life Coach
   - Analyze: freelance work, SaaS, consulting, content creation, e-commerce

2. **Life Decision** (Personal Choices)
   - Pragmatist, Dreamer, Analyst, Advisor
   - Explore: job changes, relocation, career pivots, commitments

### ✨ User Experience
- Adaptive questionnaires based on scenario type
- Loading indicator with realistic wait time
- ⏹ Stop button to abort debate anytime
- ✅ Completion banner when agents finish
- Continue debate with new information
- Export analysis results

## Technology

| Component | Tech |
|-----------|------|
| Backend | Flask + Python 3.11 |
| Frontend | Vanilla JS + HTML/CSS (responsive) |
| LLM | Claude 3.5 Sonnet via OpenRouter |
| Deployment | Docker + Cloudflare Tunnel |
| Proxy | Unified server (frontend + API routing) |

## Quick Start

### Local Development

```bash
# 1. Clone & setup
git clone https://github.com/chetan25/mirofish-scenario-engine.git
cd mirofish-scenario-engine

# 2. Install dependencies
pip install -r requirements.txt

# 3. Create .env file
cat > .env << EOF
OPENROUTER_API_KEY=your-api-key-here
EOF

# 4. Start backend (port 5001)
python mirofish_scenario_engine.py

# 5. Start frontend (port 3000)
python unified_server.py

# 6. Open browser
open http://localhost:3000/scenario-engine.html
```

### Docker Deployment

```bash
# Set API key
export OPENROUTER_API_KEY=your-key

# Start services
docker-compose up -d

# Access on http://localhost:3000
```

### Public URL (Cloudflare Tunnel)

```bash
# Terminal 1: Start backend
python mirofish_scenario_engine.py

# Terminal 2: Start frontend
python unified_server.py

# Terminal 3: Create tunnel
cloudflared tunnel --no-autoupdate --url http://localhost:3000
# Copy the generated URL to share
```

## API Endpoints

### POST `/debate`
Start multi-agent debate
```json
{
  "scenario_type": "side_hustle",
  "context": {
    "idea": "freelance writing",
    "motivation": "extra income",
    "capital": 500,
    "time": 15,
    "skills": "marketing",
    "constraints": "full-time job",
    "timeline": "6 months",
    "goal": "$2k/month"
  }
}
```

Response:
```json
{
  "debate": [
    {
      "agent": "Entrepreneur",
      "icon": "🚀",
      "perspective": "[Agent's analysis...]"
    }
  ],
  "consensus": "[Overall assessment...]"
}
```

### POST `/debate/continue`
Continue debate with new input
```json
{
  "scenario_type": "side_hustle",
  "context": {...},
  "user_input": "But I have no initial connections in this field"
}
```

### GET `/questionnaire/{scenario_type}`
Get contextual questions for a scenario
- Returns questions to ask user before debate

### GET `/health`
Health check
- Returns: `{status: "ok", agents: 8, ...}`

## How It Works

```
1. User selects scenario type
   ↓
2. Answer contextual questions
   ↓
3. Backend spawns 4 agents
   ↓
4. Each agent reasons independently with LLM
   ↓
5. Frontend parses outputs into structured format
   (Extracts: Key insight, Pros, Cons, Recommendation)
   ↓
6. Display debate & consensus
   ↓
7. User can continue with new context
```

## Output Parsing

LLM generates narrative → Frontend intelligently extracts:
- **Key Insight** - First sentence
- **Pros** - Sentences with "opportunity", "potential", "growth"
- **Cons** - Sentences with "risk", "challenge", "concern"
- **Recommendation** - Tone analysis (Go/Caution/No-Go)

This ensures clean, actionable output even if LLM doesn't follow exact format.

## File Structure

```
mirofish-scenario-engine/
├── scenario-engine.html          # Main UI (24 KB)
├── mirofish_scenario_engine.py   # Backend API
├── unified_server.py             # Frontend proxy
├── docker-compose.yml            # Docker orchestration
├── Dockerfile.backend            # Backend container
├── Dockerfile.frontend           # Frontend container
├── proxy.py                       # Request proxy handler
├── run.sh                         # Quick start script
├── requirements.txt              # Python dependencies
└── README.md                      # This file
```

## Configuration

### Backend (.env)
```
OPENROUTER_API_KEY=sk-or-v1-...     # Required
LLM_MODEL=anthropic/claude-3.5-sonnet
FLASK_ENV=production
```

### Frontend
- Responsive mobile-first CSS
- CORS-safe API calls through unified proxy
- Single-file deployment (no separate CDN)

## Deployment Options

| Option | Best For | Setup |
|--------|----------|-------|
| Local | Development | `python mirofish_scenario_engine.py && python unified_server.py` |
| Docker | Production | `docker-compose up -d` |
| Tunnel | Sharing | `cloudflared tunnel --url http://localhost:3000` |
| Cloud | Always-on | Deploy to Heroku/Railway/AWS |

## Example Scenarios

### Side Hustle: Freelance Writing
- **Idea**: Offer copywriting services
- **Capital**: $500 (website, tools)
- **Time**: 15 hrs/week
- **Skills**: 3 years marketing experience
- **Goal**: $2k/month in 6 months

### Life Decision: Job Change
- **Decision**: Switch to startup as CTO
- **Current**: Senior role at stable company
- **New**: Equity + lower cash at 5-person startup
- **Fear**: Leaving security, failing startup
- **Success**: Building product people use

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "Backend Connection Failed" | Check port 5001, verify .env has API key |
| "Debate takes too long" | Normal (10-20s for 4 LLM calls), can hit Stop |
| "API 401 Unauthorized" | Verify OPENROUTER_API_KEY in .env is valid |
| "Large output text" | Frontend parses & structures automatically |
| "Can't connect through tunnel" | Verify cloudflared is running, check tunnel URL |

## Performance

- **Debate time**: 10-20 seconds (4 parallel LLM calls)
- **UI updates**: Real-time as agents finish
- **API response**: <100ms for questionnaires
- **Proxy overhead**: ~50ms

## Future Enhancements

- [ ] Debate history & storage
- [ ] Scenario comparison (side-by-side)
- [ ] Custom agent personas
- [ ] Real-time collaboration (multi-user)
- [ ] PDF/CSV export with visualizations
- [ ] Mobile app with app store deployment
- [ ] Fine-tuned models for domain expertise
- [ ] Agent vs agent head-to-head debates

## Architecture Notes

### Why Unified Proxy?
- Frontend on tunnel (port 3000)
- Backend local (port 5001)
- Single tunnel URL handles both
- No CORS issues
- Stateless, scalable

### Agent Design
- Each agent gets full context
- Temperature 0.2 for consistent reasoning
- Max tokens 200 to keep focused
- Claude for better instruction following

### Frontend Resilience
- Graceful LLM output parsing
- Heuristic keyword extraction
- Fallback to generic pros/cons
- Works with imperfect model outputs

## Contributing

This is a personal project. For questions or suggestions, reach out.

## License

MIT

---

**Built with**: Python, Flask, Claude AI, Cloudflare
