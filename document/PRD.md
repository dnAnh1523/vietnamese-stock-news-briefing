# PRD: Vietnamese Stock News Briefing API

## 1. Bài toán
Nhà đầu tư cá nhân Việt Nam không có thời gian và công cụ để theo dõi liên tục tin tức, phân tích mức độ ảnh hưởng của từng sự kiện đến cổ phiếu họ đang quan tâm, và tổng hợp thành insight có thể hành động ngay. 
## 2. User & Use case
User: Các nhà đầu tư cá nhân
Usecase: Nhập mã cổ phiếu, nhận bản briefing — tin tức 7 ngày gần nhất + phân tích mức độ ảnh hưởng + điểm rủi ro/cơ hội nổi bật 
## 3. Input / Output
Input: mã cổ phiếu
Output: Bản briefing — tin tức 7 ngày gần nhất + phân tích mức độ ảnh hưởng + điểm rủi ro/cơ hội nổi bật 
Output format:
{
  "ticker": "HPG",
  "period": "2026-05-28 to 2026-06-04",
  "summary": "Tuần qua HPG ghi nhận...",
  "key_events": [...],
  "impact_level": "medium/high/low/None",
  "risk_flags": [...],
  "opportunity_flags": [...]
}
## 4. Data sources
CafeF, thư viện vnstock 
## 5. Kiến trúc agents
User (POST /analyze?ticker=HPG)
        ↓
   Orchestrator
        ↓
[Scraper Agent] → crawl CafeF
        ↓
[Analyst Agent] → phân tích tin, đánh giá mức độ ảnh hưởng
   (nếu thiếu context giá → báo Orchestrator → Scraper fetch vnstock)
        ↓
[Report Agent] → tổng hợp thành briefing có cấu trúc
        ↓
   JSON response trả về API

## 6. Tech stack
FastAPI, LangGraph, Gemini 2.0 Flash, requests + BeautifulSoup, vnstock
## 7. Constraints
free tier hoàn toàn, không có GPU, Windows 11, không có budget cho paid API.