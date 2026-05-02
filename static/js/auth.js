/* ═══════════════════════════════════════════════════════════
   MR SPARTA COACH OS — AUTH JAVASCRIPT
   auth.js  |  login · register · 404
═══════════════════════════════════════════════════════════ */
'use strict';

/* ── 1. EMBERS ──────────────────────────────────────────── */
(function initEmbers() {
  const container = document.getElementById('embers');
  if (!container) return;
  const COUNT = 20;
  const frag  = document.createDocumentFragment();
  for (let i = 0; i < COUNT; i++) {
    const el   = document.createElement('div');
    el.className = 'ember';
    const size  = Math.random() * 2.5 + 0.8;
    el.style.cssText = `
      left:${Math.random() * 100}%;
      bottom:0;
      width:${size}px;
      height:${size}px;
      animation-duration:${Math.random() * 9 + 6}s;
      animation-delay:${Math.random() * 14}s;
      --dx:${(Math.random() - .5) * 120}px;
    `;
    frag.appendChild(el);
  }
  container.appendChild(frag);
})();

/* ── 2. ROLE CARD SELECTION ─────────────────────────────── */
(function initRoleCards() {
  const cards = document.querySelectorAll('.role-card');
  cards.forEach(card => {
    const radio = card.querySelector('input[type="radio"]');
    if (!radio) return;

    card.addEventListener('click', () => {
      cards.forEach(c => c.classList.remove('selected'));
      card.classList.add('selected');
      radio.checked = true;
      radio.dispatchEvent(new Event('change', { bubbles: true }));
    });

    /* Keyboard support */
    card.addEventListener('keydown', e => {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        card.click();
      }
    });
    card.setAttribute('tabindex', '0');
    card.setAttribute('role', 'radio');

    if (radio.checked) card.classList.add('selected');
  });
})();

/* ── 3. PASSWORD TOGGLE ─────────────────────────────────── */
(function initPasswordToggle() {
  document.querySelectorAll('.input-toggle[data-target]').forEach(btn => {
    btn.addEventListener('click', () => {
      const input = document.getElementById(btn.dataset.target);
      if (!input) return;
      const isText = input.type === 'text';
      input.type   = isText ? 'password' : 'text';
      btn.textContent = isText ? '👁' : '🙈';
    });
  });
})();

/* ── 4. PASSWORD STRENGTH ───────────────────────────────── */
(function initPasswordStrength() {
  const input  = document.getElementById('id_password1') || document.getElementById('id_password');
  const bars   = document.querySelectorAll('.pw-bar');
  const label  = document.querySelector('.pw-label');
  if (!input || !bars.length) return;

  function getStrength(pw) {
    let score = 0;
    if (pw.length >= 8)                     score++;
    if (pw.length >= 12)                    score++;
    if (/[A-Z]/.test(pw))                   score++;
    if (/[0-9]/.test(pw))                   score++;
    if (/[^A-Za-z0-9]/.test(pw))            score++;
    return score;
  }

  const LEVELS = [
    { max:1, cls:'weak',   txt:'Débil' },
    { max:3, cls:'medium', txt:'Media' },
    { max:5, cls:'strong', txt:'Fuerte' },
  ];

  input.addEventListener('input', () => {
    const score = getStrength(input.value);
    const level = LEVELS.find(l => score <= l.max) || LEVELS[2];
    const filled = score === 0 ? 0 : score <= 1 ? 1 : score <= 3 ? 2 : 3;

    bars.forEach((bar, i) => {
      bar.className = 'pw-bar';
      if (i < filled) bar.classList.add(level.cls);
    });

    if (label) {
      label.textContent = input.value ? level.txt : '';
      label.style.color = level.cls === 'weak'
        ? 'var(--txt-err)'
        : level.cls === 'medium'
          ? 'var(--gold-lo)'
          : '#3DBB77';
    }
  });
})();

/* ── 5. FORM VALIDATION ─────────────────────────────────── */
(function initValidation() {
  const form = document.querySelector('.auth-form');
  if (!form) return;

  /* Mark fields */
  function markError(input, msg) {
    input.classList.add('error');
    let errEl = input.closest('.form-group')?.querySelector('.field-error');
    if (!errEl) {
      errEl = document.createElement('div');
      errEl.className = 'field-error';
      input.closest('.input-wrap')?.after(errEl);
    }
    errEl.textContent = msg;
  }
  function clearError(input) {
    input.classList.remove('error');
    const errEl = input.closest('.form-group')?.querySelector('.field-error');
    if (errEl) errEl.textContent = '';
  }

  /* Clear on focus */
  form.querySelectorAll('.form-input').forEach(input => {
    input.addEventListener('focus', () => clearError(input));
  });

  /* Password confirm match */
  const pw1 = document.getElementById('id_password1');
  const pw2 = document.getElementById('id_password2');
  if (pw2) {
    pw2.addEventListener('blur', () => {
      if (pw1 && pw2.value && pw1.value !== pw2.value) {
        markError(pw2, 'Las contraseñas no coinciden.');
      }
    });
  }

  /* Submit handler */
  form.addEventListener('submit', function (e) {
    let valid = true;
    const required = form.querySelectorAll('.form-input[required]');

    required.forEach(input => {
      if (!input.value.trim()) {
        markError(input, 'Este campo es obligatorio.');
        valid = false;
      }
    });

    /* Email format */
    const email = form.querySelector('input[type="email"]');
    if (email && email.value && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.value)) {
      markError(email, 'Ingresa un email válido.');
      valid = false;
    }

    /* Terms checkbox */
    const terms = form.querySelector('#id_terms');
    if (terms && !terms.checked) {
      const err = terms.closest('.form-check');
      if (err) err.style.color = 'var(--txt-err)';
      valid = false;
    }

    if (!valid) {
      e.preventDefault();
      return;
    }

    /* Loading state */
    const btn = form.querySelector('.btn-submit');
    if (btn) btn.classList.add('loading');
  });
})();

/* ── 6. AUTO-DISMISS DJANGO MESSAGES ────────────────────── */
(function initMessages() {
  const items = document.querySelectorAll('.msg-item');
  items.forEach((item, i) => {
    setTimeout(() => {
      item.style.transition = 'opacity .5s, transform .5s';
      item.style.opacity    = '0';
      item.style.transform  = 'translateY(-8px)';
      setTimeout(() => item.remove(), 500);
    }, 4000 + i * 500);
  });
})();

/* ── 7. 404 EFFECTS ─────────────────────────────────────── */
(function init404() {
  const num = document.querySelector('.num-404');
  if (!num) return;

  /* Parallax on mouse move */
  document.addEventListener('mousemove', (e) => {
    const cx = window.innerWidth  / 2;
    const cy = window.innerHeight / 2;
    const dx = (e.clientX - cx) / cx;
    const dy = (e.clientY - cy) / cy;
    num.style.transform = `translate(${dx * 8}px, ${dy * 5}px)`;
  });
})();

/* ── 8. INPUT FLOAT LABEL EFFECT ────────────────────────── */
(function initFloatLabels() {
  document.querySelectorAll('.form-input').forEach(input => {
    function update() {
      const group = input.closest('.form-group');
      if (!group) return;
      group.classList.toggle('has-value', !!input.value);
    }
    input.addEventListener('input', update);
    update();
  });
})();
