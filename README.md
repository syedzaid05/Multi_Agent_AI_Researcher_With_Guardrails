# Multi-Agent AI Researcher With Guardrails

A secure, multi-agent research assistant built with **LangGraph**. It decomposes a
research question into a plan, gathers evidence from Wikipedia and the web, analyzes
and critiques the evidence, then synthesizes a final answer with inline citations —
all wrapped in **input and output guardrails** to defend against prompt injection and
hallucinated sources.

The pipeline can run either as an interactive **Streamlit web app** or from the
**command line**.

---

## Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Agent Pipeline](#agent-pipeline)
- [Guardrails](#guardrails)
- [Project Structure](#project-structure)
- [Requirements](#requirements)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
  - [Web app (Streamlit)](#web-app-streamlit)
  - [Command line](#command-line)
- [Configuration Reference](#configuration-reference)
- [How It Works](#how-it-works)
- [Security Notes](#security-notes)
- [Troubleshooting](#troubleshooting)

---

## Features

- **Multi-agent orchestration** with LangGraph state machine.
- **Planner agent** that breaks a question into a plan plus focused search queries.
- **Dual retrieval** from Wikipedia (REST + MediaWiki API) and web search
  (Tavily primary, DuckDuckGo fallback).
- **Analysis agent** that structures findings, evidence, agreements, contradictions,
  and gaps — with numbered source references.
- **Critic agent** that flags unsupported claims, contradictions, gaps, and signs of
  injected instructions being followed.
- **Synthesis agent** that produces the final cited answer and resolves critique points.
- **Input guardrails**: length checks, control-character stripping, and prompt-injection
  pattern detection.
- **Output guardrails**: citation validation against real references and annotation of
  uncited or dangling citations.
- **Untrusted data fencing**: retrieved content is wrapped in `<untrusted-data>` tags and
  explicitly treated as data, not instructions.
- **Model fallback**: uses Gemini when available and automatically falls back to Groq.
- **Two interfaces**: a Streamlit UI and a CLI.

---

## Architecture

```
START
  │
  ▼
input_guardrails ──(blocked)──► END
  │
 (continue)
  ▼
planner ──┬──► wikipedia ────┐
          └──► web_search ───┤
                             ▼
                          analysis
                             │
                             ▼
                           critic
                             │
                             ▼
                         synthesis
                             │
                             ▼
                      output_guardrails
                             │
                             ▼
                            END
```

State is carried through a `GraphState` TypedDict (`src/state.py`). The `wikipedia`,
`web`, and `guardrail_notes` fields use an `add` reducer so parallel branches and
multiple notes accumulate rather than overwrite.

---

## Agent Pipeline

| Stage | Module | Description |
| --- | --- | --- |
| Input guardrails | `src/nodes/guard_nodes.py` | Sanitizes and validates the raw query; can block it. |
| Planner | `src/nodes/planner.py` | Returns JSON with `plan` and `research_tasks`. |
| Wikipedia | `src/nodes/research.py` / `src/tools/wikipedia.py` | Searches Wikipedia and fetches page summaries. |
| Web search | `src/nodes/research.py` / `src/tools/web_search.py` | Tavily first, DuckDuckGo fallback. |
| Analysis | `src/nodes/analysis.py` | Structures evidence and assigns numbered references. |
| Critic | `src/nodes/critic.py` | Reviews analysis for weaknesses and injection compliance. |
| Synthesis | `src/nodes/synthesis.py` | Produces the final cited answer. |
| Output guardrails | `src/nodes/guard_nodes.py` | Validates citations and normalizes references. |

The planner, Wikipedia, and web search run in a fan-out/fan-in pattern around the
analysis node; the critic and synthesis stages run as a linear chain using the
Gemini-or-Groq fallback wrapper in `src/llm.py`.

---

## Guardrails

### Input guardrails (`src/guardrails.py::check_input`)

- Strips control characters.
- Enforces `MIN_QUERY_LEN` and `MAX_QUERY_LEN`.
- Scans for common prompt-injection patterns (e.g. "ignore previous instructions",
  "reveal your system prompt", "jailbreak", chat/role control tokens).
- Blocked queries short-circuit the graph and return a safe refusal message.

### Untrusted-data fencing (`src/utils.py::fence_untrusted`)

Retrieved source content is wrapped in `<untrusted-data>...</untrusted-data>` tags. Every
downstream system prompt instructs the model to treat that content strictly as data.

### Output guardrails (`src/guardrails.py::finalize_output`)

- Extracts inline citations (`[1]`, `[2]`, ...).
- Validates each cited id against the real reference list.
- Records notes when a citation has no matching reference or when the final answer has
  no inline citations at all.

---

## Project Structure

```
Multi_Agent_AI_Reseacher_With_Guardrails/
├── app.py                  # Streamlit web interface
├── main.py                 # Command-line interface
├── requirements.txt        # Python dependencies
├── .env                    # API keys (not committed)
├── src/
│   ├── config.py           # Env loading, model names, key validation
│   ├── graph.py            # LangGraph construction
│   ├── guardrails.py       # Input/output guardrail logic
│   ├── llm.py              # LLM factories + Gemini→Groq fallback
│   ├── state.py            # GraphState TypedDict
│   ├── utils.py            # Message parsing, source numbering, fencing
│   ├── nodes/
│   │   ├── analysis.py     # Analysis agent
│   │   ├── critic.py       # Critic agent
│   │   ├── guard_nodes.py  # Input/output guard nodes
│   │   ├── planner.py      # Planner agent
│   │   ├── research.py     # Wikipedia + Web search nodes
│   │   └── synthesis.py    # Synthesis agent
│   └── tools/
│       ├── web_search.py   # Tavily + DuckDuckGo search
│       └── wikipedia.py    # Wikipedia search + summaries
```

---

## Requirements

- Python 3.10+
- API keys for:
  - **Groq** (`GROQ_API_KEY`) — required (used by planner and analysis, and as fallback)
  - **Google Gemini** (`GEMINI_API_KEY`) — required by the key check; used for critic/synthesis
  - **Tavily** (`TAVILY_API_KEY`) — required by the key check; primary web search

> DuckDuckGo search works without a key, but the app still requires the Tavily key to
> pass `require_keys()`.

---

## Installation

```powershell
# Clone the repository
git clone <repository-url>
cd Multi_Agent_AI_Reseacher_With_Guardrails

# Create and activate a virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

---

## Configuration

Create a `.env` file in the project root:

```dotenv
GROQ_API_KEY="your-groq-api-key"
GEMINI_API_KEY="your-gemini-api-key"
TAVILY_API_KEY="your-tavily-api-key"

# Optional model overrides
PLANNER_MODEL="openai/gpt-oss-120b"
ANALYSIS_MODEL="openai/gpt-oss-120b"
CRITIC_MODEL="gemini-3.8-flash"
SYNTHESIS_MODEL="gemini-3.8-flash"

# Optional guardrail limits
MAX_QUERY_LEN="4000"
MIN_QUERY_LEN="3"
```

`src/config.py` loads this file via `python-dotenv` and `require_keys()` reports any
missing required keys before the pipeline runs.

---

## Usage

### Web app (Streamlit)

```powershell
streamlit run app.py
```

Then open the shown local URL, enter a research question, and click **Run**. The UI
streams each node as it completes and displays the answer, plan, references, cited ids,
and any guardrail notes.

### Command line

```powershell
python main.py "What are the security risks of prompt injection in LLM agents?"
```

You can also run it with no arguments to be prompted interactively:

```powershell
python main.py
```

The CLI prints the final answer, plan, references, cited ids, and guardrail notes.

---

## Configuration Reference

| Variable | Default | Description |
| --- | --- | --- |
| `GROQ_API_KEY` | — | Groq API key (required). |
| `GEMINI_API_KEY` | — | Google Gemini API key (required by key check). |
| `TAVILY_API_KEY` | — | Tavily API key (required by key check). |
| `PLANNER_MODEL` | `openai/gpt-oss-120b` | Model for the planner agent (Groq). |
| `ANALYSIS_MODEL` | `openai/gpt-oss-120b` | Model for the analysis agent and fallback. |
| `CRITIC_MODEL` | `gemini-3.8-flash` | Model for the critic agent. |
| `SYNTHESIS_MODEL` | `gemini-3.8-flash` | Model for the synthesis agent. |
| `MAX_QUERY_LEN` | `4000` | Maximum accepted query length. |
| `MIN_QUERY_LEN` | `3` | Minimum accepted query length. |

---

## How It Works

1. The raw query passes through **input guardrails** for sanitization and validation.
2. The **planner** decomposes the query into a short plan and 2–5 search queries.
3. The planner's tasks fan out to the **Wikipedia** and **web search** nodes in parallel.
4. Retrieved sources are deduplicated and numbered, then fenced as untrusted data fed to
   the **analysis** agent.
5. The **critic** reviews the analysis for weaknesses and injection compliance.
6. The **synthesis** agent writes the final answer, resolving critique points and citing
   references inline.
7. **Output guardrails** validate citations and annotate any issues before display.

---

## Security Notes

- `.env` is listed in `.gitignore` and **must never be committed**. If a key has ever been
  shared or committed, rotate it immediately.
- Retrieved web/Wikipedia content is treated as untrusted and fenced; downstream prompts
  explicitly forbid following instructions found inside it.
- Output guardrails only allow citations whose ids match real retrieved references, which
  reduces fabricated-source output.
- Guardrails are heuristics, not a guarantee. Do not rely on them as the sole control for
  untrusted input in production.

---

## Troubleshooting

- **"Missing API keys in .env"** — ensure `GROQ_API_KEY`, `GEMINI_API_KEY`, and
  `TAVILY_API_KEY` are set in `.env`.
- **Gemini fallback warning on stderr** — the critic/synthesis stage fell back to Groq;
  this is expected when Gemini is unavailable.
- **No references / empty results** — search providers may be rate-limited or blocked;
  DuckDuckGo is used automatically when Tavily returns nothing.
- **Query blocked** — the input guardrail matched an injection pattern or a length limit;
  rephrase the question.

---

## License

No license file is currently included. Add one before distributing or reusing this code.
