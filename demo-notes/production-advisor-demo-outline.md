# Production Line Health Advisor Demo
## Speaker Notes Outline (25-30 minutes)

**Audience:** ASSA ABLOY team - developers, engineers, and business stakeholders
**Format:** Technical demo with live walkthrough
**Goal:** Demonstrate AI-assisted development while showing genuine technical understanding

---

## TL;DR - 10 Key Takeaways

1. **What it does:** Upload production CSV, get instant AI-powered health report with visualizations and actionable insights
2. **Built with AI assistance:** Used Claude Code heavily - transparent about this, which adds credibility rather than reducing it
3. **Architecture:** n8n (visual workflows) + FastAPI + Ollama (local LLM) - your data never leaves your network
4. **Why "agentic":** LLM decides what analysis to run based on data, not hardcoded steps - adapts to different datasets
5. **Two tools:** `analyze_data` (failure rates, risk factors, high-risk machines) and `create_chart` (visualizations)
6. **The loop:** LLM calls tool → gets results → reflects → decides if more needed → repeats until done
7. **Business value:** Instant insights vs. waiting for manual analysis; non-technical users can ask follow-up questions
8. **Trade-offs:** Local LLM = privacy + no API costs, but slightly lower quality than GPT-4/Claude
9. **Where it shines:** Exploratory analysis, flexible input, rapid prototyping. **Where it struggles:** High-throughput, deterministic requirements
10. **Honest lesson:** Powerful pattern, not magic - value comes from combining LLM reasoning with well-designed tools and domain-specific prompts

---

## Slide: When You Need This Agent

**Scenario Bullets (for PowerPoint):**

- **Instant insights:** Know which machines failed today before your shift ends — no waiting for analysts.
- **Natural language questions:** Plant managers ask "What needs maintenance?" and get answers with charts.
- **Flexible analysis:** Works with any CSV schema — no predefined reports or rigid column requirements.

**Flow Diagram (horizontal - screenshot for slides):**

```
┌────────┐    ┌────────┐    ┌─────────┐    ┌────────┐    ┌─────────────────────────────────┐    ┌────────────┐
│  User  │───▶│  n8n   │───▶│ FastAPI │───▶│ Ollama │───▶│          AGENTIC LOOP           │───▶│   Output   │
│        │    │Webhook │    │ Backend │    │ (LLM)  │    │                                 │    │            │
│CSV/Chat│    │        │    │         │    │llama3.1│    │  ┌─────────┐     ┌──────────┐  │    │• Summary   │
└────────┘    └────────┘    └─────────┘    └────────┘    │  │ Decide  │────▶│ Execute  │  │    │• Insights  │
                                                         │  │what to  │     │ Tools    │  │    │• Charts    │
                                                         │  │analyze  │◀────│          │  │    │            │
                                                         │  └─────────┘     └──────────┘  │    └────────────┘
                                                         │       ▲                        │
                                                         │       └── Reflect & Repeat ───┘│
                                                         └─────────────────────────────────┘

                                           TOOLS: analyze_data (failure_rates, risk_factors, high_risk_machines)
                                                  create_chart (failure_by_type, distributions, comparisons)

                                    ┌──────────────────────────────────────────────────────────────────────┐
                                    │  100% LOCAL: Data never leaves network • No API costs • Private AI   │
                                    └──────────────────────────────────────────────────────────────────────┘
```

---

## 1. Opening Hook (2-3 minutes)

### Main Talking Points

- "Imagine getting an instant health report on your production line the moment you upload yesterday's data. Not next week after someone manually analyzes it - *right now*."

- "Today I'm going to show you something I built in [X hours/days] that would have taken significantly longer without AI assistance. And I'm going to be completely transparent about what that means."

- "This isn't about replacing engineers - it's about giving your production teams a data analyst that never sleeps and responds in seconds."

### Key Phrases for Mixed Audience

| Technical Audience | Business Audience |
|-------------------|-------------------|
| "Agentic LLM architecture" | "AI that can think through problems step-by-step" |
| "Local inference with Ollama" | "Your data never leaves your servers" |
| "Tool-calling loop" | "The AI decides what analysis to run based on what it finds" |

### The Hook Question

"How long does it currently take to get actionable insights from your production data? What if that could happen while you're still uploading the file?"

### Transition

"Let me show you exactly how this works, starting with how I actually built it."

---

## 2. The AI Development Story (5-7 minutes)

### Opening Statement

"I want to be upfront: I used Claude Code heavily to build this. But I think that transparency actually makes this demo *more* valuable, not less. Here's why."

### What AI-Assisted Development Actually Means

- "This isn't 'AI wrote my code and I don't understand it.' It's more like pair programming with a very fast junior developer who has read every Python tutorial ever written."

- "I directed the architecture. I made the design decisions. The AI helped me move faster on implementation."

### Specific Examples from This Project

**What AI Did Well:**

- "FastAPI boilerplate and endpoint structure - took minutes instead of an hour"
- "Matplotlib visualization code - I described what I wanted, got working charts quickly"
- "Tool definition schemas for Ollama function calling - the JSON structure is tedious to write manually"
- "Docker Compose configuration - networking between containers is easy to mess up"

**What Required Human Judgment:**

- "Architecture decision: Why an agent with tools vs. a hardcoded pipeline? I had to understand the trade-offs."
- "The system prompt for manufacturing context - AI can generate prompts, but knowing what matters for ASSA ABLOY required domain understanding"
- "Choosing Ollama over cloud APIs - that's a policy and cost decision, not a coding one"
- "Column name flexibility in the analysis code - anticipating that different sites name things differently"

### Honest Time Estimates

> **Technical Aside (if asked):**
> "The core agent loop in `core.py` is about 180 lines. The tool definitions and execution logic is another 130 lines. With AI assistance, this took roughly [X hours]. Without it, I'd estimate [2-3x longer]. The AI didn't make it *possible* - it made it *faster*."

### What This Means for ASSA ABLOY

- "This approach lets smaller teams punch above their weight"
- "Proof of concepts can be validated in days, not weeks"
- "The question isn't 'Can we use AI to build tools?' - it's 'What should we build first?'"

### Transition

"Now let me walk you through *what* we built and *why* the architecture looks the way it does."

---

## 3. Architecture Walkthrough (5-7 minutes)

### Visual Aid Suggestion

Draw or show a simple diagram:

```
[CSV Upload] -> [n8n Workflow] -> [FastAPI + Agent] -> [Ollama LLM]
                                        |
                                 [Analysis Tools]
                                        |
                                 [Visualization Tools]
```

### Why n8n for Workflow Orchestration

**For Technical Audience:**
- "n8n gives us webhook endpoints without writing HTTP server code"
- "Visual workflow makes it easier to add steps later - email notifications, database logging, etc."
- "It's self-hosted, which matters for data governance"

**For Business Audience:**
- "Think of n8n as the 'front door' - it receives your CSV uploads and routes them to the right place"
- "Non-technical team members can see the workflow visually and even make simple changes"
- "No vendor lock-in - this runs on your infrastructure"

### Why FastAPI + Ollama (Local LLM)

**The Key Point:**
"Your production data never leaves your network. There are no API calls to OpenAI or Anthropic. The LLM runs locally."

**Technical Details:**
- "FastAPI because it's fast, modern Python with automatic API documentation"
- "Ollama because it makes running open-source LLMs trivially easy - one Docker container"
- "Currently using Mistral/Llama 3.1 - can swap models without code changes"

**Business Implications:**
- "No per-token costs - once it's running, it's running"
- "No data leaving your firewall"
- "Can run on modest hardware - doesn't require a GPU cluster"

### Why Agent Architecture (vs. Hardcoded Pipeline)

**The Traditional Approach:**
"You could build this as: Upload -> Always run analysis A -> Always run analysis B -> Always make chart C -> Return results"

**The Agent Approach:**
"Instead: Upload -> Ask the LLM 'what analysis would be helpful?' -> LLM decides -> Execute -> LLM reflects on results -> Decides if more analysis needed -> Repeat until done"

**Why This Matters:**
- "If someone uploads a dataset without a 'failure_type' column, a hardcoded pipeline breaks. The agent adapts."
- "Follow-up questions work naturally - 'Show me just the machines from Line 3' doesn't require a new workflow"
- "The same architecture scales to new types of analysis without rewriting the pipeline"

### Transition

"Let me show you exactly how that tool-calling loop works in practice."

---

## 4. Tool Integration Deep Dive (5-7 minutes)

### What "Agentic" Means in Simple Terms

"When I say 'agentic,' I mean the LLM doesn't just answer questions - it takes actions."

**Analogy for Business Audience:**
"Think of it like the difference between asking someone 'What's 2+2?' versus asking 'Here's a spreadsheet, figure out what's interesting and show me.' The second one requires initiative, judgment, and the ability to use tools."

### The Tool-Calling Loop Explained

Walk through this step-by-step:

1. **User uploads CSV** -> System tells LLM "Here's what the data looks like, run initial analysis"

2. **LLM decides what to do** -> "I should call `analyze_data` with `analysis_type='all'` to get the full picture"

3. **System executes the tool** -> Python code runs, returns statistics to LLM

4. **LLM reflects on results** -> "The failure rate is 4.2%. That's concerning. I should visualize this."

5. **LLM calls another tool** -> "Call `create_chart` with `chart_type='failure_by_type'`"

6. **System executes chart generation** -> Returns base64 image

7. **LLM decides it has enough** -> Writes final response with insights

**Key Code Reference (show if technical audience is engaged):**

```python
# From core.py - the agent loop
while iterations < max_iterations:
    response = self.client.chat(
        model=self.model,
        messages=[...],
        tools=TOOLS,  # These are the tools the LLM can call
    )

    tool_calls = message.get("tool_calls", [])
    if not tool_calls:
        break  # LLM is done, no more tools needed

    # Execute each tool the LLM requested
    for tool_call in tool_calls:
        result = execute_tool(tool_name, tool_args, df, cache)
        # Feed result back to LLM
```

### The Actual Tools

**analyze_data Tool:**
- Takes an `analysis_type` parameter: `failure_rates`, `risk_factors`, `high_risk_machines`, `failure_types`, or `all`
- Returns structured data the LLM can reason about
- Caches results so the LLM can reference them later

**create_chart Tool:**
- Takes a `chart_type` parameter: `failure_by_type`, `risk_factors`, `failure_distribution`, `machine_comparison`
- Returns base64-encoded PNG that gets included in the response
- Uses cached analysis data when available (efficiency)

### Why This Is More Powerful Than Hardcoded Workflows

| Hardcoded Pipeline | Agent with Tools |
|-------------------|------------------|
| Always runs same analysis | Adapts to what's in the data |
| Breaks on unexpected input | Gracefully handles missing columns |
| New analysis = new code | New analysis = new tool (modular) |
| Can't answer follow-ups | Conversational by design |
| One output format | LLM crafts response to context |

### Technical Aside (if asked about prompts)

"The system prompt in `prompts.py` is specifically tuned for manufacturing context. It knows to lead with critical findings, quantify everything, and provide actionable recommendations. That's the domain expertise baked in."

```python
# From prompts.py
SYSTEM_PROMPT = """You are a Production Line Health Advisor...
CONTEXT: You're helping ASSA ABLOY (global leader in access solutions)...
- Lead with the most critical findings
- Quantify everything with specific numbers from the data
- Provide actionable recommendations, not just observations
"""
```

### Transition

"Enough theory - let me show you this actually working."

---

## 5. Live Demo (5-7 minutes)

### Pre-Demo Checklist

- [ ] Docker containers running (`docker-compose up`)
- [ ] n8n accessible at `http://localhost:5678`
- [ ] Sample CSV ready (`data/sample_production.csv` or similar)
- [ ] Ollama model pulled and ready
- [ ] Browser tabs pre-loaded: n8n, API docs at `http://localhost:8000/docs`

### Demo Flow with Talking Points

#### Step 1: Show the n8n Workflow (30 seconds)

**What to Show:**
- Open n8n at `http://localhost:5678`
- Navigate to "Production Line Analysis" workflow
- Show the three nodes: Webhook -> FastAPI Call -> Return Response

**What to Say:**
"This is our entry point. A simple three-step workflow: receive the file, send it to our analysis engine, return the results. Anyone can understand this at a glance."

#### Step 2: Upload a CSV (1-2 minutes)

**What to Show:**
- Use curl, Postman, or the n8n test feature
- Upload a sample production CSV

**What to Say:**
"I'm uploading a CSV with [X] records of production data - machine IDs, failure indicators, timestamps, sensor readings. In a real deployment, this could come from your MES system, a scheduled export, or even a manual upload."

**Command (if using curl):**
```bash
curl -X POST http://localhost:5678/webhook/production-analyze \
  -F "file=@sample_production.csv"
```

#### Step 3: Show the Response (2-3 minutes)

**What to Show:**
- The JSON response with summary, insights, and charts
- Decode a base64 chart to show visualization

**What to Say:**
"Look at what came back. Executive summary, specific metrics, and - here's the key part - the AI *decided* to create these specific charts because it found them relevant to the findings."

**Point out specifically:**
- The failure rate percentage
- High-risk machines identified
- The fact that charts are embedded as base64 (no external image hosting needed)

#### Step 4: Ask a Follow-Up Question (1-2 minutes)

**What to Show:**
- Use the chat workflow or API endpoint
- Ask something like: "Which machines should we prioritize for maintenance this week?"

**What to Say:**
"Now watch what happens when we ask a follow-up. The agent remembers the data we uploaded. It doesn't need to re-analyze from scratch."

**What to Say About the Response:**
"Notice it's not just repeating the earlier analysis. It's *reasoning* about the question using the data it already has."

### Backup Plans

**If Ollama is slow:**
"You'll notice there's some latency here - that's the LLM thinking. In production, you'd tune this based on your latency vs. quality trade-offs. Smaller models are faster, larger models are smarter."

**If something fails:**

| Failure | Recovery |
|---------|----------|
| Container not running | "Let me restart that quickly - this is why we have health check endpoints" |
| Model not loaded | "The first request loads the model into memory - subsequent requests are faster" |
| CSV parsing error | "This actually demonstrates something useful - the system fails gracefully with a clear error message" |

**If the analysis seems wrong:**
"This is actually a great learning moment. The LLM is reasoning about the data, but it's not perfect. This is why we designed it to show its work - you can see exactly what analysis it ran."

### Transition

"Now let me share some honest reflections on what I learned building this."

---

## 6. Lessons Learned (3-5 minutes)

### What I Would Do Differently

**Start with the data schema earlier:**
"I built generic column detection, but in hindsight, I'd partner with the team using this to define a standard schema. Flexibility is good, but predictability is often better."

**More robust error handling:**
"The happy path works great. Edge cases need more work - what happens when someone uploads a file with 2 million rows? We'd need chunking, streaming, or size limits."

**Add confidence indicators:**
"The LLM sounds confident even when it shouldn't be. I'd add explicit uncertainty markers - 'Based on limited data...' or 'This correlation may be spurious because...'"

### Challenges Encountered

**Local LLM quality vs. cloud APIs:**
"Honestly, GPT-4 or Claude would give better analysis. Ollama models are good, but there's a quality gap. The trade-off is privacy and cost vs. raw capability."

**Tool schema iteration:**
"Getting the tool definitions right took several attempts. The LLM needs clear, unambiguous parameter descriptions or it guesses wrong."

**Session management:**
"Keeping conversation context across requests required explicit session tracking. This is solved, but it's not obvious when you start."

### Where This Approach Shines

- **Exploratory analysis:** "What's wrong?" questions where you don't know what you're looking for
- **Flexible input:** Different datasets with different columns
- **Natural language interface:** Non-technical users can ask questions
- **Rapid prototyping:** Getting from idea to working demo quickly

### Where This Approach Struggles

- **High-throughput scenarios:** LLM inference isn't instant
- **Deterministic requirements:** If you need *exactly* the same output every time, hardcode it
- **Complex multi-step reasoning:** Agents can get confused on very complex tasks
- **Auditability:** "Why did it conclude X?" is harder to answer than with rule-based systems

### Honest Assessment

"This is a powerful pattern, but it's not magic. The value comes from combining LLM reasoning with well-designed tools and domain-specific prompting. Any one piece alone isn't enough."

### Transition

"I'll stop there. What questions do you have?"

---

## 7. Q&A Preparation

### Anticipated Questions and Answers

#### Technical Questions

**Q: "What model are you using?"**
A: "Currently [Mistral/Llama 3.1/etc.] through Ollama. The architecture is model-agnostic - we can swap models by changing one config value. Trade-off is always speed vs. quality."

**Q: "How would this scale to millions of rows?"**
A: "Right now it loads everything into memory. For larger datasets, we'd add chunking, sampling strategies, or pre-aggregation. The analysis functions would need to work with database queries instead of DataFrames."

**Q: "Can we add new types of analysis?"**
A: "Yes - add a new function in `production.py`, add a new entry in the `TOOLS` list in `tools.py`, and the LLM will automatically have access to it. That's the benefit of the agent pattern."

**Q: "What about hallucinations?"**
A: "The tools return real data - the LLM can't make up numbers that aren't in the output. The risk is misinterpretation. We mitigate by showing our work and being explicit about confidence."

**Q: "Why n8n instead of just FastAPI endpoints?"**
A: "You could skip n8n entirely. We included it because: (1) Visual workflows for non-developers, (2) Easy to add notification nodes later, (3) Shows how this integrates with existing automation tools."

#### Business Questions

**Q: "What's the cost to run this?"**
A: "Initial setup: development time. Ongoing: just compute. Ollama runs on a modest server - no per-query API costs. Compare to paying for data analyst time."

**Q: "How long until production ready?"**
A: "This is a proof of concept. Production would need: authentication, rate limiting, logging, monitoring, schema standardization with your systems. Estimate [X weeks/months] depending on requirements."

**Q: "Where else could we use this pattern?"**
A: "Any domain where you have data + questions. Quality inspection analysis, supply chain optimization, maintenance scheduling, energy consumption analysis. The pattern is generic, the prompts and tools are specific."

**Q: "What if the analysis is wrong?"**
A: "It shows its work - you can see what data led to what conclusion. Treat it like a smart intern: valuable insights, but verify important decisions. Don't automate critical decisions without human review."

**Q: "Does this replace our data analysts?"**
A: "It augments them. They go from 'running queries' to 'validating insights and making decisions.' Higher-value work."

#### Meta Questions

**Q: "You mentioned using AI to build this - should we be concerned about code quality?"**
A: "I reviewed every line. AI-assisted doesn't mean unreviewed. Think of it like using Stack Overflow answers - you still need to understand what you're putting in your codebase. The code is straightforward Python that any developer can maintain."

**Q: "Is this approach mature enough for enterprise use?"**
A: "The individual pieces are battle-tested: FastAPI, Ollama, n8n, Python. The pattern of 'LLM + tools' is newer but well-documented. Start with low-stakes use cases and build confidence."

---

## Appendix: Technical Reference

### Key Files Quick Reference

| File | Purpose |
|------|---------|
| `docker-compose.yml` | Orchestrates n8n + FastAPI containers |
| `app/main.py` | FastAPI endpoints: `/health`, `/webhook/analyze`, `/webhook/chat` |
| `app/agent/core.py` | Agent loop: LLM calls, tool execution, session management |
| `app/agent/tools.py` | Tool definitions and execution logic |
| `app/agent/prompts.py` | System prompt with ASSA ABLOY context |
| `app/analysis/production.py` | Statistical analysis functions |
| `app/analysis/visualizations.py` | Chart generation (matplotlib -> base64) |
| `n8n/workflows/01-production-analysis.json` | CSV upload workflow |
| `n8n/workflows/02-production-chat.json` | Chat follow-up workflow |

### Architecture Decisions Summary

| Decision | Rationale |
|----------|-----------|
| Local LLM (Ollama) | Data privacy, no API costs |
| Agent pattern | Flexibility, natural language interface |
| Session-based state | Multi-turn conversations |
| Base64 images | No external image hosting needed |
| Tool caching | Efficiency, consistent results |
| n8n as frontend | Visual workflows, easy extensions |

### Running the Demo

```bash
# Start all services
docker-compose up -d

# Check health
curl http://localhost:8000/health

# Upload CSV for analysis
curl -X POST http://localhost:5678/webhook/production-analyze \
  -F "file=@data/sample_production.csv"

# Follow-up chat (use session_id from previous response)
curl -X POST http://localhost:5678/webhook/production-chat \
  -H "Content-Type: application/json" \
  -d '{"session_id": "YOUR_SESSION_ID", "message": "Which machines need attention?"}'
```

---

## Timing Summary

| Section | Duration |
|---------|----------|
| Opening Hook | 2-3 min |
| AI Development Story | 5-7 min |
| Architecture Walkthrough | 5-7 min |
| Tool Integration Deep Dive | 5-7 min |
| Live Demo | 5-7 min |
| Lessons Learned | 3-5 min |
| **Total (before Q&A)** | **25-36 min** |
| Q&A Buffer | 5-10 min |

**Tip:** The middle sections (Architecture, Tools, Demo) can be compressed if running long. The Opening and Lessons Learned should stay intact - they're what makes this presentation memorable.

---

*Last updated: 2026-01-19*
*Project: Production Line Health Advisor*
*Presenter notes for ASSA ABLOY demo*
