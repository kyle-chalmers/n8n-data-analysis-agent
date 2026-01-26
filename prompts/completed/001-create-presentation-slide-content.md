<objective>
Create presentation materials for a PowerPoint slide explaining when the Production Line Health Advisor agent would be needed.

Deliverables:
1. Three concise bullet points describing a real-world scenario
2. A simple ASCII flow diagram of the system architecture
</objective>

<context>
This is for a workshop demo presentation to ASSA ABLOY stakeholders showcasing AI agent capabilities.

The Production Line Health Advisor is an AI-powered data analysis agent that:
- Accepts CSV uploads of manufacturing/production data
- Uses a local LLM (Ollama + llama3.1) to analyze failure rates, risk factors, and quality issues
- Generates visualizations and actionable insights
- Supports conversational follow-up questions
- Runs 100% locally (no data leaves the network, no API costs)

Architecture: n8n webhooks → FastAPI backend → Ollama LLM (agentic loop with tools)

Key files to reference for accurate details:
@demo-notes/production-advisor-demo-outline.md
@app/agent/core.py
@app/agent/tools.py
</context>

<requirements>
**Bullet Points:**
- Exactly 3 bullet points
- Each should describe a compelling scenario/use case
- Written for mixed technical/business audience
- Focus on business value, not technical implementation
- Concise enough for a presentation slide (1-2 sentences each)

**Flow Diagram:**
- ASCII art format (monospace-friendly for screenshot)
- Show the key components: User → n8n → FastAPI → Ollama → Tools → Output
- Highlight the "agentic loop" where LLM decides what to analyze
- Include the available tools (analyze_data, create_chart)
- Keep it simple enough to understand at a glance
</requirements>

<output>
Output directly to the conversation (do not create files).

Format:
1. A header "Scenario: When You Need a Production Health Advisor Agent"
2. The 3 bullet points with brief titles in bold
3. A header "Flow Diagram"
4. The ASCII diagram in a code block
</output>

<success_criteria>
- Bullet points are specific to THIS project (not generic AI agent scenarios)
- Diagram accurately reflects the n8n + FastAPI + Ollama architecture
- Content is presentation-ready (can be copied directly into PowerPoint)
- ASCII diagram renders cleanly when screenshot with monospace font
</success_criteria>
