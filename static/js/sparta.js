/* ═══════════════════════════════════════════════════════════════
   MR SPARTA COACH OS — UNIFIED JAVASCRIPT
   sparta.js  |  Single JS for Coach + Athlete dashboards
═══════════════════════════════════════════════════════════════ */
'use strict';

/* ── 1. CLOCK ─────────────────────────────────────────────── */
function initClock() {
  const el = document.getElementById('clock');
  if (!el) return;
  const days = ['Dom','Lun','Mar','Mié','Jue','Vie','Sáb'];
  function tick() {
    const n = new Date();
    const d = days[n.getDay()];
    const h = String(n.getHours()).padStart(2,'0');
    const m = String(n.getMinutes()).padStart(2,'0');
    const s = String(n.getSeconds()).padStart(2,'0');
    el.textContent = `${d} ${h}:${m}:${s}`;
  }
  tick(); setInterval(tick, 1000);
}

/* ── 2. SIDEBAR COLLAPSE ───────────────────────────────────── */
function initSidebar() {
  const sidebar  = document.querySelector('.sidebar');
  const main     = document.querySelector('.main-area');
  const toggleBtn = document.getElementById('sb-toggle');
  if (!sidebar) return;

  function setCollapsed(state) {
    sidebar.classList.toggle('collapsed', state);
    if (main) main.classList.toggle('expanded', state);
    localStorage.setItem('sb_collapsed', state ? '1' : '0');
  }

  /* Restore saved state */
  const saved = localStorage.getItem('sb_collapsed');
  if (saved === '1') setCollapsed(true);

  if (toggleBtn) {
    toggleBtn.addEventListener('click', () => {
      setCollapsed(!sidebar.classList.contains('collapsed'));
    });
  }

  /* Mobile overlay */
  const mobileToggle = document.getElementById('mobile-sb-toggle');
  if (mobileToggle) {
    mobileToggle.addEventListener('click', () => {
      sidebar.classList.toggle('mobile-open');
    });
  }

  /* Close on outside click (mobile) */
  document.addEventListener('click', (e) => {
    if (window.innerWidth > 768) return;
    if (!sidebar.contains(e.target) && mobileToggle && !mobileToggle.contains(e.target)) {
      sidebar.classList.remove('mobile-open');
    }
  });
}

/* ── 3. PAGE NAVIGATION ───────────────────────────────────── */
function initNav() {
  const items = document.querySelectorAll('.sb-item[data-page]');
  const pages = document.querySelectorAll('.page');

  function showPage(id) {
    pages.forEach(p => p.classList.toggle('active', p.id === `page-${id}`));
    items.forEach(i => i.classList.toggle('active', i.dataset.page === id));
    /* Update topbar breadcrumb */
    const bc = document.getElementById('bc-page');
    if (bc) bc.textContent = id.charAt(0).toUpperCase() + id.slice(1).replace(/-/g,' ');
    /* Close mobile sidebar */
    document.querySelector('.sidebar')?.classList.remove('mobile-open');
  }

  items.forEach(item => {
    item.addEventListener('click', () => showPage(item.dataset.page));
  });

  /* Activate first page by default */
  const first = items[0];
  if (first) showPage(first.dataset.page);
}

/* ── 4. RING CHARTS ───────────────────────────────────────── */
function initRings() {
  document.querySelectorAll('[data-ring]').forEach(el => {
    const pct = parseInt(el.dataset.ring, 10);
    const r   = 40;
    const circ= 2 * Math.PI * r;
    const fill= el.querySelector('.ring-fill');
    if (!fill) return;
    fill.setAttribute('stroke-dasharray', circ);
    /* Animate in */
    fill.setAttribute('stroke-dashoffset', circ);
    setTimeout(() => {
      fill.setAttribute('stroke-dashoffset', circ - (circ * pct / 100));
    }, 300);
  });
}

/* ── 5. PROGRESS BAR WIDTHS ──────────────────────────────── */
function initProgressBars() {
  document.querySelectorAll('[data-fill]').forEach(el => {
    const val = el.dataset.fill;
    el.style.width = '0%';
    setTimeout(() => { el.style.width = val + '%'; }, 400);
  });
}

/* ── 6. WEIGHT CHART ─────────────────────────────────────── */
function renderWeightChart(weights, containerId, axisId) {
  const chart = document.getElementById(containerId);
  const axis  = document.getElementById(axisId);
  if (!chart || !weights.length) return;

  const mn = Math.min(...weights) - 1;
  const mx = Math.max(...weights) + 1;
  const rng= mx - mn;

  chart.innerHTML = weights.map((w, i) => {
    const pct = ((w - mn) / rng) * 100;
    const hi  = i === weights.length - 1 ? ' hi' : '';
    return `<div class="w-bar-wrap"><div class="w-bar${hi}" style="height:${pct}%" title="${w}kg"></div></div>`;
  }).join('');

  if (axis) {
    axis.innerHTML = weights.map(w => `<span>${w}</span>`).join('');
  }
}

/* ── 7. COUNTER ANIMATION ────────────────────────────────── */
function animateCounter(el, target, suffix, dur = 1600) {
  const start = performance.now();
  function step(now) {
    const p = Math.min((now - start) / dur, 1);
    const e = 1 - Math.pow(1 - p, 3);
    const v = Math.round(target * e);
    el.textContent = v + suffix;
    if (p < 1) requestAnimationFrame(step);
  }
  requestAnimationFrame(step);
}

/* ── 8. MODAL ────────────────────────────────────────────── */
function initModals() {
  document.querySelectorAll('[data-modal-open]').forEach(btn => {
    btn.addEventListener('click', () => {
      const id = btn.dataset.modalOpen;
      const overlay = document.getElementById(id);
      if (overlay) overlay.classList.add('open');
    });
  });
  document.querySelectorAll('[data-modal-close], .modal-overlay').forEach(el => {
    el.addEventListener('click', (e) => {
      if (e.target === el) {
        el.closest('.modal-overlay')?.classList.remove('open');
        if (el.dataset.modalClose) {
          document.getElementById(el.dataset.modalClose)?.classList.remove('open');
        }
      }
    });
  });
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
      document.querySelectorAll('.modal-overlay.open').forEach(o => o.classList.remove('open'));
    }
  });
}

/* ── 9. CHAT ──────────────────────────────────────────────── */
function initChat() {
  const inputs = document.querySelectorAll('.chat-input-send');
  inputs.forEach(form => {
    const input   = form.querySelector('.chat-input');
    const sendBtn = form.querySelector('.send-btn');
    const msgArea = form.closest('.chat-shell')?.querySelector('.chat-messages')
                 || form.closest('.chat-wrap')?.querySelector('.chat-messages')
                 || document.querySelector('.chat-messages');
    if (!input || !msgArea) return;

    function send() {
      const text = input.value.trim();
      if (!text) return;
      const div = document.createElement('div');
      div.className = 'msg out';
      div.innerHTML = `
        <div class="msg-av">YO</div>
        <div>
          <div class="msg-bubble">${text}</div>
          <div class="msg-ts">Ahora</div>
        </div>`;
      msgArea.appendChild(div);
      msgArea.scrollTop = msgArea.scrollHeight;
      input.value = '';
    }

    if (sendBtn) sendBtn.addEventListener('click', send);
    input.addEventListener('keydown', e => { if (e.key === 'Enter') send(); });
  });
}

/* ── 10. AI CHAT ─────────────────────────────────────────── */
const AI_RESPONSES = {
  default: 'Analizando datos de tus clientes... Con base en el progreso registrado esta semana, tengo 3 recomendaciones específicas.',
  riesgo:  'Detecté 5 clientes en riesgo: Ana García (cumplimiento 58%), Luis Torres (sin datos 14 días), Roberto Díaz (estancado), Claudia Mora (plan vence), Pedro Soto (3 sesiones incompletas).',
  analizar:'Juan Martínez — Semana 12: bajó 4.8kg desde inicio. Cumplimiento 96%. Sugerencia: +5kg en sentadillas, mantener calorías.',
  ajustes: 'Ajustes sugeridos: Roberto → +200kcal/día. Claudia → renovar plan. Pedro → reducir a 4 días/semana.',
  resumen: '24 clientes activos. Cumplimiento promedio 78%. Mejor: Sofía 97%. Mayor riesgo: Ana 58%. 3 planes ajustados esta semana.',
};

function initAIChat() {
  const areas = document.querySelectorAll('.ai-chat-area');
  areas.forEach(area => {
    const input   = area.querySelector('.ai-input');
    const sendBtn = area.querySelector('.ai-send');
    const msgs    = area.querySelector('.ai-messages');
    if (!input || !msgs) return;

    function ask(query) {
      const userDiv = document.createElement('div');
      userDiv.className = 'msg out';
      userDiv.style.maxWidth = '90%';
      userDiv.innerHTML = `<div class="msg-av">TU</div><div><div class="msg-bubble">${query}</div></div>`;
      msgs.appendChild(userDiv);

      setTimeout(() => {
        const key = Object.keys(AI_RESPONSES).find(k => query.toLowerCase().includes(k)) || 'default';
        const aiDiv = document.createElement('div');
        aiDiv.className = 'msg';
        aiDiv.style.maxWidth = '90%';
        aiDiv.innerHTML = `
          <div class="msg-av" style="background:linear-gradient(135deg,#8B6914,#C9A84C)">AI</div>
          <div><div class="msg-bubble" style="background:rgba(201,168,76,.05);border-color:rgba(201,168,76,.18)">${AI_RESPONSES[key]}</div>
          <div class="msg-ts">Spartan AI</div></div>`;
        msgs.appendChild(aiDiv);
        msgs.scrollTop = msgs.scrollHeight;
      }, 700);

      msgs.scrollTop = msgs.scrollHeight;
      if (input) input.value = '';
    }

    if (sendBtn) sendBtn.addEventListener('click', () => { if (input.value.trim()) ask(input.value.trim()); });
    if (input) input.addEventListener('keydown', e => { if (e.key === 'Enter' && input.value.trim()) ask(input.value.trim()); });

    /* Quick buttons */
    area.querySelectorAll('.ai-quick-btn').forEach(btn => {
      btn.addEventListener('click', () => ask(btn.textContent));
    });
  });
}

/* ── 11. WORKOUT CHECK TOGGLE ────────────────────────────── */
function initWorkoutChecks() {
  document.querySelectorAll('.wd-check').forEach(el => {
    el.addEventListener('click', () => {
      const done = el.classList.toggle('done');
      el.textContent = done ? '✓' : '';
    });
  });
}

/* ── 12. CLIENT SELECTOR (progress page) ─────────────────── */
function initClientSelector() {
  const items = document.querySelectorAll('.client-sel-item');
  items.forEach(item => {
    item.addEventListener('click', () => {
      items.forEach(i => i.classList.remove('active'));
      item.classList.add('active');
      /* Update chart & stats from data attrs */
      const w = JSON.parse(item.dataset.weights || '[]');
      const name = item.dataset.name || '';
      const peso = item.dataset.peso || '';
      const cumpl = parseInt(item.dataset.cumpl || 0);
      const sem  = item.dataset.sem || '';

      const pName = document.getElementById('prog-client-name');
      if (pName) pName.textContent = `📊 ${name} — Evolución de Peso`;

      const pPeso  = document.getElementById('s-peso');
      const pCumpl = document.getElementById('s-cumpl');
      const pSem   = document.getElementById('s-sem');
      if (pPeso)  pPeso.textContent  = peso;
      if (pCumpl) pCumpl.textContent = cumpl + '%';
      if (pSem)   pSem.textContent   = sem;

      if (w.length) renderWeightChart(w, 'weight-chart', 'weight-axis');

      /* Update ring */
      const ring = document.getElementById('prog-ring-fill');
      if (ring) {
        const circ = 2 * Math.PI * 40;
        ring.setAttribute('stroke-dasharray', circ);
        ring.setAttribute('stroke-dashoffset', circ - (circ * cumpl / 100));
        ring.className = 'ring-fill' + (cumpl < 65 ? ' red' : cumpl > 85 ? ' green' : '');
      }
      const ringLabel = document.getElementById('prog-ring-label');
      if (ringLabel) ringLabel.textContent = cumpl + '%';
    });
  });

  /* Trigger first */
  if (items[0]) items[0].click();
}

/* ── 13. NOTIFICATION TOAST ──────────────────────────────── */
function showToast(msg, type = 'gold') {
  const toast = document.createElement('div');
  toast.style.cssText = `
    position:fixed; bottom:24px; right:24px; z-index:9999;
    background:var(--panel); border:1px solid var(--border2);
    border-left:2px solid var(--${type === 'red' ? 'red' : type === 'green' ? 'green' : 'gold'});
    padding:12px 18px; font-size:12px; color:var(--txt);
    font-family:var(--font-b); letter-spacing:.3px;
    animation:fadeUp .3s ease; max-width:320px;
    box-shadow:0 8px 32px rgba(0,0,0,.4);
  `;
  toast.textContent = msg;
  document.body.appendChild(toast);
  setTimeout(() => toast.remove(), 3500);
}

/* ── 14. SEARCH FILTER (client table) ────────────────────── */
function initSearch() {
  const searchInput = document.getElementById('client-search');
  if (!searchInput) return;
  searchInput.addEventListener('input', () => {
    const q = searchInput.value.toLowerCase();
    document.querySelectorAll('#clients-tbody tr').forEach(row => {
      const name = row.querySelector('.c-name')?.textContent.toLowerCase() || '';
      row.style.display = name.includes(q) ? '' : 'none';
    });
  });
}

/* ── INIT ALL ─────────────────────────────────────────────── */
document.addEventListener('DOMContentLoaded', () => {
  initClock();
  initSidebar();
  initNav();
  initRings();
  initProgressBars();
  initModals();
  initChat();
  initAIChat();
  initWorkoutChecks();
  initClientSelector();
  initSearch();

  /* Default weight chart for coach progress page */
  renderWeightChart(
    [89,88.2,87.5,87,86.8,86.2,85.8,85.5,85.1,84.8,84.5,84.2],
    'weight-chart', 'weight-axis'
  );

  /* Athlete weight chart */
  renderWeightChart(
    [84,83.5,83,82.4,82,81.6,81.2,80.9],
    'ath-weight-chart', 'ath-weight-axis'
  );

  /* Counter animations */
  document.querySelectorAll('[data-count]').forEach(el => {
    const observer = new IntersectionObserver(entries => {
      if (entries[0].isIntersecting) {
        animateCounter(el, parseInt(el.dataset.count), el.dataset.suffix || '');
        observer.disconnect();
      }
    });
    observer.observe(el);
  });

  /* Quick action buttons on alert cards */
  document.querySelectorAll('.alert-apply').forEach(btn => {
    btn.addEventListener('click', e => {
      e.stopPropagation();
      showToast('✓ Ajuste aplicado correctamente', 'green');
      btn.closest('.alert-card')?.remove();
    });
  });
});
