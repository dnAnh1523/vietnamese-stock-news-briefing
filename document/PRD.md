# Product Requirements Document: Vietnamese Stock News Briefing

## 1. Overview

Vietnamese Stock News Briefing is a full-stack AI application that helps users quickly understand recent news impact for a Vietnamese stock ticker.

The user enters a ticker such as `HPG`, `FPT`, or `VNM`. The system validates the ticker, collects recent CafeF news, enriches the analysis with recent market price context from `vnstock`, and returns a structured briefing with:

- Summary
- Key events
- Estimated impact level
- Risk flags
- Opportunity flags

The product is designed for a small free-tier deployment using a static frontend on Netlify and a FastAPI backend on Render.

> This product is an information summarization aid, not financial advice.

## 2. Problem Statement

Retail investors in Vietnam often follow many tickers at once, but stock-related news is fragmented and noisy. A single ticker can have multiple recent articles across earnings, corporate actions, market sentiment, insider transactions, macro policy, and general PR.

The core problem is not only finding the news. The harder part is quickly answering:

- What happened recently?
- Is the news specific enough to matter?
- Is the likely impact high, medium, low, or unclear?
- What risks and opportunities are explicitly supported by the articles?
- Is recent price movement consistent with the news context?

The product compresses this workflow into one ticker input and one structured response.

## 3. Target Users

### Primary User

Individual Vietnamese retail investor who wants a quick briefing before doing deeper research.

### Secondary User

Student, analyst, or developer evaluating how LLM agents can combine scraping, market data, and structured output for financial-news workflows.

## 4. Goals

### Product Goals

- Let users generate a stock-news briefing from a single ticker input.
- Focus the analysis on recent, source-grounded news rather than generic market commentary.
- Present the output in a simple UI that is easy to scan.
- Keep the system deployable on free tiers.

### Technical Goals

- Provide a typed FastAPI API with clear request and response contracts.
- Use LangGraph to orchestrate multi-step analysis rather than a single monolithic function.
- Validate tickers before running expensive scraping and LLM calls.
- Add fallback behavior when scraping, price lookup, LLM formatting, or source data is incomplete.
- Keep the project testable with pytest.

## 5. Non-Goals

- Provide buy/sell recommendations.
- Replace professional financial research.
- Guarantee real-time market data.
- Cover all Vietnamese news sources.
- Provide portfolio tracking, alerts, watchlists, authentication, or user accounts.
- Support high-traffic production scale in the current version.

## 6. User Experience

### Main Flow

1. User opens the web UI.
2. User enters a ticker symbol.
3. Frontend sends `POST /analyze?ticker=<ticker>`.
4. Backend normalizes the ticker to uppercase.
5. Backend validates ticker syntax and exchange existence.
6. LangGraph workflow gathers news, fetches price context, analyzes content, and formats the response.
7. Frontend renders the briefing.

### Frontend States

Current implementation supports:

- Empty input feedback
- Loading state while analysis runs
- Error box for API or network failures
- Result view with:
  - Ticker
  - Period
  - Summary
  - Impact badge
  - Key events
  - Risk flags
  - Opportunity flags

### Expected User Inputs

Valid examples:

- `HPG`
- `FPT`
- `VNM`

Invalid examples:

- Empty input
- Symbols with punctuation, e.g. `HPG!`
- Unknown ticker, e.g. `ZZZZZ`

## 7. Functional Requirements

### FR1: Ticker Validation

The system must:

- Strip whitespace.
- Convert ticker to uppercase.
- Reject empty ticker values.
- Reject invalid formats using `^[A-Z0-9]{1,10}$`.
- Validate ticker existence through `vnstock`.
- Return `404` when a ticker does not exist on HOSE, HNX, or UPCOM.

### FR2: News Collection

The system must:

- Query CafeF for multiple news types.
- Use ticker-based article search.
- Filter articles by a configurable date window.
- Deduplicate articles by detail link or title.
- Fetch article content when available.
- Retry with a wider time window when not enough articles are found.

Current configuration:

- `DEFAULT_DAYS = 7`
- `DEFAULT_PAGESIZE = 20`
- `MIN_ARTICLES = 3`
- `MAX_RETRIES = 3`

### FR3: Price Context

The system must:

- Validate exchange metadata with `vnstock`.
- Fetch recent historical price data.
- Return:
  - Ticker
  - Exchange
  - Latest close
  - Weekly percentage change
  - Period start
  - Period end
  - Trading day count
- Return a structured error object if price data is unavailable.

### FR4: Agentic Analysis

The system must use a LangGraph workflow with the following nodes:

- `scraper`
- `analyst`
- `price`
- `report`

The `analyst` node controls whether the workflow needs:

- More news data
- Price context
- Final report generation

### FR5: LLM Reasoning and Formatting

The system must:

- Use Groq chat completions.
- Use model `llama-3.3-70b-versatile`.
- Make one reasoning call for analysis.
- Make one formatting call to convert reasoning into JSON.
- Reject or repair invalid JSON by falling back to a safe structured response.
- Avoid unsupported generic claims where source evidence is insufficient.

### FR6: Structured Report

The API must return a response matching `BriefingResponse`:

```json
{
  "ticker": "HPG",
  "period": "2026-05-29 to 2026-06-05",
  "summary": "Brief evidence-based impact summary.",
  "key_events": [
    {
      "date": "2026-06-01",
      "title": "Specific company event",
      "impact": "medium"
    }
  ],
  "impact_level": "medium",
  "risk_flags": ["Specific risk found in the news"],
  "opportunity_flags": ["Specific opportunity found in the news"]
}
```

### FR7: Static Frontend Hosting

The frontend must:

- Work when served directly by FastAPI.
- Work when hosted separately on Netlify.
- Read backend URL from `window.API_BASE_URL`.
- Fall back to same-origin API calls when no external backend URL is configured.

### FR8: Health Check

The backend must expose:

```http
GET /health
```

Response:

```json
{
  "status": "ok",
  "groq_configured": true
}
```

## 8. API Specification

### `GET /health`

Purpose: Check backend availability and whether the Groq API key is configured.

Success:

- `200 OK`

### `POST /analyze?ticker=<ticker>`

Purpose: Generate a structured stock-news briefing.

Query parameters:

| Name | Type | Required | Description |
| --- | --- | --- | --- |
| `ticker` | string | Yes | Vietnamese stock ticker, e.g. `HPG` |

Success:

- `200 OK`
- Body: `BriefingResponse`

Errors:

| Status | Cause |
| --- | --- |
| `400` | Empty or invalid ticker format |
| `404` | Unknown ticker or no usable final report |
| `503` | Missing required runtime configuration, such as `GROQ_API_KEY` |
| `500` | Unexpected graph execution failure |

## 9. System Architecture

```text
Browser UI
  |
  v
POST /analyze?ticker=HPG
  |
  v
FastAPI route
  |
  |-- ticker format validation
  |-- vnstock ticker validation
  |
  v
LangGraph workflow
  |
  |-- Scraper Agent  -> CafeF article list and content
  |-- Price Agent    -> vnstock exchange and price context
  |-- Analyst Agent  -> Groq reasoning and JSON formatting
  `-- Report Agent   -> response normalization
  |
  v
BriefingResponse JSON
  |
  v
Frontend result view
```

## 10. Agent Responsibilities

### Scraper Agent

Input:

- Ticker
- Retry count
- Existing articles

Responsibilities:

- Query CafeF article lists.
- Filter by time window.
- Deduplicate articles.
- Fetch article body content.
- Increase retry count.

Output:

- Updated article list
- Updated retry count
- `need_more_data = false`

### Analyst Agent

Input:

- Articles
- Price context
- Ticker

Responsibilities:

- Request more scraping if fewer than `MIN_ARTICLES` articles are available.
- Request price data if missing.
- Build the LLM user prompt with article text and price context.
- Call Groq for reasoning.
- Call Groq again for JSON formatting.
- Fallback safely if LLM call or JSON parsing fails.

Output:

- Analysis JSON string
- Routing flags

### Price Agent

Input:

- Ticker

Responsibilities:

- Fetch ticker exchange.
- Fetch recent price history.
- Compute recent percentage change.
- Return structured price context or structured error.

Output:

- `price_context`
- `need_price_data = false`

### Report Agent

Input:

- Articles
- Analysis JSON string
- Ticker

Responsibilities:

- Parse formatted analysis.
- Normalize `key_events`.
- Generate final response period.
- Return safe fallback report when articles or analysis are missing.

Output:

- `final_report`

## 11. Data Sources

### CafeF

Used for:

- Article metadata
- Article title
- Subtitle
- Article content
- Deploy date

Current scraper behavior:

- Uses CafeF AJAX news endpoint.
- Queries multiple news types.
- Adds browser-like user agent.
- Applies request timeouts.
- Skips malformed article dates.

### vnstock

Used for:

- Ticker validation
- Exchange lookup
- Recent historical price context

### Groq

Used for:

- LLM reasoning
- JSON formatting

Required environment variable:

```env
GROQ_API_KEY=your_key_here
```

## 12. Prompting Requirements

The analyst prompt must:

- Treat the model as a Vietnamese stock analyst.
- Use only provided article information and price context.
- Classify catalysts by event type.
- Require concrete evidence for claims.
- Avoid generic statements when evidence is insufficient.
- Output analysis that can be converted into the response schema.

The formatting prompt must:

- Convert reasoning into valid JSON.
- Avoid adding new information.
- Return only JSON.

## 13. Non-Functional Requirements

### Reliability

- Invalid tickers must fail before scraping or LLM calls.
- CafeF request failures should not crash the whole app.
- Missing price data should become structured context, not an uncaught exception.
- Invalid LLM JSON should fall back to a safe response.

### Performance

- Designed for low-volume free-tier usage.
- No GPU requirement.
- Render free-tier cold starts are accepted.
- Synchronous scraping is acceptable for demo scope but not ideal for high traffic.

### Security

- `GROQ_API_KEY` must not be committed.
- `.env` must remain ignored by Git.
- CORS is currently permissive for deployment simplicity.

### Maintainability

- Keep agents separated by responsibility.
- Keep API models typed with Pydantic.
- Keep frontend static and framework-free.
- Keep tests focused on behavior rather than external network dependencies.

## 14. Deployment Requirements

### Backend

Target: Render free tier

Configuration:

- Python runtime
- `pip install -r requirements.txt`
- `uvicorn api.routes:app --host 0.0.0.0 --port $PORT`
- Required env var: `GROQ_API_KEY`

### Frontend

Target: Netlify free tier

Configuration:

- Base directory: `frontend`
- Static publish output
- Runtime API config through generated `js/config.js`
- Required env var: `API_BASE_URL`

### Combined Mode

FastAPI can also serve the static frontend directly from `/`, `/css`, and `/js`.

## 15. Testing Requirements

Current automated tests cover:

- API health route
- Ticker validation errors
- Unknown ticker behavior
- Successful analyze route with mocked graph
- Missing final report behavior
- Index page serving
- LangGraph routing decisions
- Report agent JSON parsing and fallback behavior
- Prompt builder price-context integration
- `vnstock` ticker validation and price context helpers

Command:

```bash
pytest tests/ -v
```

## 16. Success Metrics

### Product Metrics

- User can generate a briefing from a valid ticker.
- Invalid ticker errors are clear.
- Result is readable and structured.
- Output includes both risk and opportunity sections.

### Technical Metrics

- Test suite passes locally.
- Backend deploys successfully on Render.
- Frontend deploys successfully on Netlify.
- API response matches `BriefingResponse`.
- No API key leakage in repository.

## 17. Current Limitations

- CafeF availability and response format can change.
- `vnstock` availability and schema can change.
- LLM output quality depends on source article quality.
- Synchronous scraping can be slow.
- Render free tier can cold start.
- No caching is currently implemented.
- No user authentication or watchlist support.
- No source citations are rendered in the frontend yet.

## 18. Roadmap

### Near-Term

- Add source links to rendered key events.
- Add better loading/cold-start messaging in the frontend.
- Add caching for repeated ticker requests.
- Add CI test workflow on GitHub.
- Add stricter CORS configuration for known frontend domains.

### Mid-Term

- Add more Vietnamese financial news sources.
- Add article-level citation display.
- Add request rate limiting.
- Add async scraping.
- Add persistent storage for recent briefings.

### Long-Term

- Add watchlists and scheduled briefings.
- Add email or Telegram notifications.
- Add comparative ticker analysis.
- Add portfolio-level news summaries.
- Add evaluation dataset for financial-news impact quality.

## 19. Open Questions

- Should the product stay as a single-ticker briefing tool or expand into watchlists?
- Should the frontend expose raw sources and article links by default?
- What is the minimum acceptable number of articles for low-news tickers?
- Should price movement influence impact level or only provide context?
- Should future versions include Vietnamese-language output, English output, or both?
