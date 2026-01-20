<objective>
Create a 20-30 minute demo speaker notes outline for presenting the Production Line Health Advisor n8n workflow to a mixed technical/business ASSA ABLOY audience.

The outline should demonstrate:
1. How AI tools (Claude Code) accelerated development
2. Architecture decisions and why they make sense for manufacturing
3. How agentic tool-calling works in practice
4. Live demo talking points
5. Honest lessons learned

The presenter wants to be transparent about AI-assisted development while demonstrating genuine technical understanding.
</objective>

<context>
Project being demoed: Production Line Health Advisor
- n8n workflow that accepts CSV uploads of production data
- FastAPI backend with Ollama (local LLM) for analysis
- Agent architecture with tool-calling (analyze_data, create_chart tools)
- Session-based chat for follow-up questions
- Generates visualizations and actionable insights

Key files to understand:
- ./n8n/workflows/01-production-analysis.json - CSV upload workflow
- ./n8n/workflows/02-production-chat.json - Chat follow-up workflow
- ./app/main.py - FastAPI endpoints
- ./app/agent/core.py - Agent loop implementation
- ./app/agent/tools.py - Tool definitions
- ./app/agent/prompts.py - System prompts (ASSA ABLOY context built in)
- ./docker-compose.yml - Full stack deployment

Audience: ASSA ABLOY team - mixed technical (developers, engineers) and business stakeholders interested in AI/automation for manufacturing optimization.

Presentation format: Speaker notes/outline with talking points (not slides)
Includes: Live demo walkthrough
</context>

<requirements>
Create the outline with these sections:

1. **Opening Hook (2-3 min)**
   - Why this matters for manufacturing/ASSA ABLOY
   - What you'll show them

2. **The AI Development Story (5-7 min)**
   - Be honest: "I used AI heavily to build this"
   - What that actually means in practice
   - What AI did well vs what required human judgment
   - Time savings (be specific if possible)

3. **Architecture Walkthrough (5-7 min)**
   - Why n8n for workflow orchestration (visual, no-code friendly, webhooks)
   - Why FastAPI + Ollama (local LLM = data stays on-prem, no API costs)
   - Why agent architecture with tools vs direct LLM calls
   - How to explain this to non-technical stakeholders

4. **Tool Integration Deep Dive (5-7 min)**
   - What "agentic" means in simple terms
   - The tool-calling loop (LLM decides what to do, executes, reflects)
   - Show the actual tools: analyze_data, create_chart
   - Why this is more powerful than hardcoded workflows

5. **Live Demo (5-7 min)**
   - Talking points for each step
   - What to show in n8n UI
   - What to show in API response
   - Backup plan if something fails

6. **Lessons Learned (3-5 min)**
   - What would you do differently
   - Challenges encountered
   - Where this approach shines vs where it struggles

7. **Q&A Prep**
   - Anticipated questions and answers

Format each section with:
- Main talking points (what to say)
- Key phrases to use for mixed audience
- Technical details to mention if asked
- Transitions to next section
</requirements>

<output>
Save the complete speaker notes outline to: `./demo-notes/production-advisor-demo-outline.md`

Structure as markdown with clear headers, bullet points for talking points, and callout boxes for key phrases or technical asides.
</output>

<verification>
Before completing, verify:
- Timing adds up to approximately 25-30 minutes (with buffer for Q&A)
- Each section has clear talking points (not just headers)
- Technical content is balanced with business value
- Live demo section has specific steps and fallback plans
- Lessons learned section is honest and adds credibility
</verification>

<success_criteria>
- Outline is complete and presentation-ready
- Mixed audience can follow (business people aren't lost, technical people aren't bored)
- AI-assisted development is acknowledged without being defensive
- Architecture decisions are explained with clear "why" reasoning
- Tool integration is demystified for non-experts
- Live demo has clear steps and contingency plans
</success_criteria>
