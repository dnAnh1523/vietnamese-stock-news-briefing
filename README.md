# Vietnamese Stock News Briefing

Phân tích tin tức cổ phiếu Việt Nam 7 ngày gần nhất, đánh giá mức độ ảnh hưởng và tổng hợp briefing có cấu trúc.

## Yêu cầu

- Python 3.11+
- Windows 11 / macOS / Linux
- API key Groq (free tier)

## Cài đặt

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS/Linux

pip install -r requirements.txt
copy .env.example .env        # Windows
# cp .env.example .env        # macOS/Linux
```

Thêm `GROQ_API_KEY` vào file `.env`.

## Chạy

```bash
python main.py
```

- **UI:** http://localhost:8000
- **API:** `POST /analyze?ticker=HPG`
- **Health:** `GET /health`

## Deploy

### Backend: Render

`render.yaml` defines a free Python web service.

- Build command: `pip install -r requirements.txt`
- Start command: `uvicorn api.routes:app --host 0.0.0.0 --port $PORT`
- Required env var: `GROQ_API_KEY`
- Health check: `/health`

### Frontend: Netlify

`netlify.toml` publishes the static files in `frontend/`.

Set this Netlify environment variable after the Render backend is live:

```bash
API_BASE_URL=https://your-render-service.onrender.com
```

## Kiến trúc

```
POST /analyze
    → LangGraph Orchestrator
        → Scraper Agent (CafeF)
        → Analyst Agent (Groq LLM)
            ↳ thiếu tin → retry scraper
            ↳ thiếu giá → Price Agent (vnstock)
        → Report Agent
    → JSON briefing
```

## Output mẫu

```json
{
  "ticker": "HPG",
  "period": "2026-05-28 to 2026-06-04",
  "summary": "Tuần qua HPG ghi nhận...",
  "key_events": [{"date": "2026-06-01", "title": "...", "impact": "medium"}],
  "impact_level": "medium",
  "risk_flags": ["..."],
  "opportunity_flags": ["..."]
}
```

## Test

```bash
pytest tests/ -v
```

## Nguồn dữ liệu

- Tin tức: [CafeF](https://cafef.vn)
- Giá & mã CK: [vnstock](https://github.com/thinh-vu/vnstock)
