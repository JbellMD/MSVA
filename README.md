# Multi-Agent Startup Validation Assistant (MSVA)

A collaborative multi-agent system designed to help aspiring founders validate their startup ideas through comprehensive analysis of market trends, competitor products, target audience demand, and potential MVP feature sets.

## 🎯 Project Objective

To help aspiring founders validate their startup idea by analyzing:
- Market trends
- Competitor products
- Target audience demand
- Potential MVP feature sets

## 👥 Agents & Their Roles

1. 🧠 **Market Researcher Agent**
   - Goal: Conduct web search & trend analysis on startup idea
   - Tool Use: Web Search Tool, Trend Analyzer
   - Output: Summary of current market interest, growth direction, and industry signals

2. 🧾 **Competitor Analyzer Agent**
   - Goal: Search for and summarize existing solutions
   - Tool Use: Web Scraper, RAG tool for comparing competitors
   - Output: Breakdown of 2-3 competitors, features, weaknesses, and pricing models

3. 👤 **Customer Persona Generator Agent**
   - Goal: Build user personas and hypothesize user needs
   - Tool Use: Custom prompt template engine, Demographic API (optional), Persona Synthesizer
   - Output: At least 2 detailed personas with pain points and usage behaviors

4. 🛠️ **MVP Planner Agent**
   - Goal: Define a minimal feature set and suggest tech stack
   - Tool Use: Vector Search of prior MVPs, Estimation Calculator Tool
   - Output: Prioritized MVP feature list, rough cost estimate, launch timeline

## 🔌 Tool Integrations

- **Web Search Tool**: For real-time trend and competitor discovery
- **Scraper Tool**: To extract and summarize content from competitor websites
- **RAG Retriever (Vector Search)**: To suggest relevant MVP features from prior successful projects
- **Custom Cost Estimator Tool**: To calculate MVP cost estimate based on API calls or logic rules

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- API keys for OpenAI and Serper/SerpAPI (see `.env.example`)

### Installation
1. Clone the repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Set up environment variables:
   ```
   cp .env.example .env
   # Edit .env file with your API keys
   ```

### Running the Application
```
python main.py --idea "Your startup idea description"
```

## 📋 Example Workflow

1. User inputs startup idea
2. Market Researcher Agent analyzes market trends
3. Competitor Analyzer Agent identifies and summarizes existing solutions
4. Customer Persona Generator Agent creates detailed user personas
5. MVP Planner Agent suggests feature set and tech stack
6. User approves or refines the MVP plan
7. System generates a comprehensive validation report

## 📝 License
MIT License
