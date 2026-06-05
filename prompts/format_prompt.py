"""Format prompt — chuyển reasoning thành JSON chuẩn."""


FORMAT_SYSTEM = """Bạn là JSON formatter. Nhiệm vụ duy nhất: đọc phân tích và convert thành JSON hợp lệ.
KHÔNG thêm thông tin mới. KHÔNG suy diễn. Chỉ extract từ phân tích được cung cấp.
Chỉ trả về JSON, không thêm bất cứ thứ gì khác."""


def build_format_prompt(ticker: str, reasoning: str) -> str:
    return f"""Từ phân tích dưới đây về mã {ticker}, extract thành JSON:

## PHÂN TÍCH
{reasoning}

## OUTPUT FORMAT
{{
    "summary": "2-3 câu tóm tắt có số liệu cụ thể",
    "key_events": [
        {{"date": "YYYY-MM-DD hoặc null", "title": "mô tả sự kiện cụ thể", "impact": "low|medium|high"}}
    ],
    "impact_level": "low|medium|high|None",
    "risk_flags": ["rủi ro cụ thể từ tin tức", "..."],
    "opportunity_flags": ["cơ hội cụ thể từ tin tức", "..."]
}}"""
