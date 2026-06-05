const API_BASE_URL = (window.API_BASE_URL || '').replace(/\/+$/, '');
const API = `${API_BASE_URL}/analyze`;

const tickerInput = document.getElementById('tickerInput');
const analyzeBtn = document.getElementById('analyzeBtn');
const errorBox = document.getElementById('errorBox');
const resultEl = document.getElementById('result');

tickerInput.addEventListener('keydown', e => {
  if (e.key === 'Enter') analyze();
});

async function parseError(res) {
  const text = await res.text();
  try {
    const json = JSON.parse(text);
    return json.detail || text;
  } catch {
    return text || `Lỗi ${res.status}`;
  }
}

async function analyze() {
  const ticker = tickerInput.value.trim().toUpperCase();
  if (!ticker) {
    tickerInput.focus();
    tickerInput.style.borderColor = 'var(--red)';
    setTimeout(() => tickerInput.style.borderColor = '', 800);
    return;
  }

  analyzeBtn.disabled = true;
  analyzeBtn.classList.add('loading');
  errorBox.classList.remove('visible');
  resultEl.classList.remove('visible');

  try {
    const res = await fetch(`${API}?ticker=${encodeURIComponent(ticker)}`, { method: 'POST' });

    if (!res.ok) {
      throw new Error(await parseError(res));
    }

    render(await res.json());
  } catch (err) {
    errorBox.textContent = `Không thể phân tích: ${err.message}`;
    errorBox.classList.add('visible');
  } finally {
    analyzeBtn.disabled = false;
    analyzeBtn.classList.remove('loading');
  }
}

function render(d) {
  document.getElementById('rTicker').textContent = d.ticker;
  document.getElementById('rPeriod').textContent = d.period;
  document.getElementById('rSummary').textContent = d.summary;

  const impactEl = document.getElementById('rImpact');
  const level = (d.impact_level || 'none').toLowerCase();
  const labels = {
    high: 'Ảnh hưởng cao',
    medium: 'Ảnh hưởng vừa',
    low: 'Ảnh hưởng thấp',
    none: 'Chưa xác định'
  };
  impactEl.textContent = labels[level] || level;
  impactEl.className = `impact-badge impact-${level}`;

  renderEvents('rEvents', d.key_events || []);
  renderList('rRisks', d.risk_flags || [], 'flag-list risk-list');
  renderList('rOpps', d.opportunity_flags || [], 'flag-list opp-list');

  resultEl.classList.remove('visible');
  void resultEl.offsetWidth;
  resultEl.classList.add('visible');

  setTimeout(() => {
    resultEl.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }, 100);
}

function renderEvents(id, events) {
  const el = document.getElementById(id);
  el.className = 'event-list';
  el.innerHTML = events.map(event => {
    if (typeof event === 'string') {
      return `<li>${escapeHtml(event)}</li>`;
    }
    const date = event.date ? `<span class="event-date">${escapeHtml(event.date)}</span>` : '';
    const impact = event.impact ? `<span class="event-impact impact-${event.impact}">${escapeHtml(event.impact)}</span>` : '';
    return `<li>${date}<span class="event-title">${escapeHtml(event.title || '')}</span>${impact}</li>`;
  }).join('');
}

function renderList(id, items, className) {
  const el = document.getElementById(id);
  el.className = className;
  el.innerHTML = items.map(item => `<li>${escapeHtml(String(item))}</li>`).join('');
}

function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}
