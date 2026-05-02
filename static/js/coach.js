/* ═══════════════════════════════════════════════════════════
   COACH — Registration JS
   coach.js
═══════════════════════════════════════════════════════════ */
(function () {
  'use strict';

  const form      = document.getElementById('coach-form');
  const submitBtn = form?.querySelector('.btn-submit');

  /* ── 1. EMBERS ──────────────────────────────────────────── */
  (function embers() {
    const container = document.getElementById('embers');
    if (!container) return;
    const frag = document.createDocumentFragment();
    for (let i = 0; i < 22; i++) {
      const el = document.createElement('div');
      el.className = 'ember';
      const s = Math.random() * 2.5 + .8;
      el.style.cssText = `
        left:${Math.random() * 100}%;
        bottom:0; width:${s}px; height:${s}px;
        animation-duration:${Math.random() * 9 + 6}s;
        animation-delay:${Math.random() * 14}s;
        --dx:${(Math.random() - .5) * 120}px;
      `;
      frag.appendChild(el);
    }
    container.appendChild(frag);
  })();

  /* ── 2. PASSWORD TOGGLE ─────────────────────────────────── */
  document.querySelectorAll('.input-toggle[data-target]').forEach(btn => {
    btn.addEventListener('click', () => {
      const input = document.getElementById(btn.dataset.target);
      if (!input) return;
      const isText = input.type === 'text';
      input.type = isText ? 'password' : 'text';
      btn.textContent = isText ? '👁' : '🙈';
    });
  });

  /* ── 3. PASSWORD STRENGTH ───────────────────────────────── */
  (function pwStrength() {
    const input = document.getElementById('id_password1');
    const bars  = document.querySelectorAll('.pw-bar');
    const label = document.querySelector('.pw-label');
    if (!input || !bars.length) return;

    const LEVELS = [
      { max: 1, cls: 'weak',   txt: 'Débil',  color: '#FF6B6B' },
      { max: 3, cls: 'medium', txt: 'Media',  color: '#C9A84C' },
      { max: 5, cls: 'strong', txt: 'Fuerte', color: '#3DBB77' },
    ];

    function scoreOf(pw) {
      let s = 0;
      if (pw.length >= 8)          s++;
      if (pw.length >= 12)         s++;
      if (/[A-Z]/.test(pw))        s++;
      if (/[0-9]/.test(pw))        s++;
      if (/[^A-Za-z0-9]/.test(pw)) s++;
      return s;
    }

    input.addEventListener('input', () => {
      const score  = scoreOf(input.value);
      const level  = LEVELS.find(l => score <= l.max) || LEVELS[2];
      const filled = score === 0 ? 0 : score <= 1 ? 1 : score <= 3 ? 2 : 3;
      bars.forEach((b, i) => {
        b.className = 'pw-bar';
        if (i < filled) b.classList.add(level.cls);
      });
      if (label) {
        label.textContent = input.value ? level.txt : '';
        label.style.color = level.color;
      }
    });
  })();

  /* ── 4. PASSWORD CONFIRM ────────────────────────────────── */
  (function pwMatch() {
    const p1 = document.getElementById('id_password1');
    const p2 = document.getElementById('id_password2');
    if (!p1 || !p2) return;

    p2.addEventListener('blur', () => {
      if (p2.value && p1.value !== p2.value) {
        markError(p2, 'Las contraseñas no coinciden.');
      } else {
        clearError(p2);
      }
    });
  })();

  /* ── 5. EMAIL LIVE VALIDATION ───────────────────────────── */
  (function emailCheck() {
    const input = document.getElementById('id_email');
    if (!input) return;

    let timeout;
    let indicator = null;

    function getIndicator() {
      if (indicator) return indicator;
      const wrap = input.closest('.input-wrap');
      indicator = document.createElement('span');
      indicator.className = 'email-status';
      wrap.appendChild(indicator);
      return indicator;
    }

    input.addEventListener('input', () => {
      clearTimeout(timeout);
      const email = input.value.trim();
      const ind   = getIndicator();
      ind.textContent = '';
      ind.className   = 'email-status';

      if (!email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) return;

      timeout = setTimeout(() => {
        ind.className   = 'email-status check';
        ind.textContent = '⟳';

        const url = form.dataset.checkEmailUrl || '/auth/api/check-email/';
        const fd  = new FormData();
        fd.append('email', email);
        fd.append('csrfmiddlewaretoken', getCSRF());

        fetch(url, { method: 'POST', body: fd })
          .then(r => r.json())
          .then(data => {
            if (data.available) {
              ind.className   = 'email-status ok';
              ind.textContent = '✓';
              clearError(input);
            } else {
              ind.className   = 'email-status err';
              ind.textContent = '✗';
              markError(input, data.message || 'Email ya registrado.');
            }
          })
          .catch(() => { ind.textContent = ''; });
      }, 500);
    });
  })();

  /* ── 6. EXPERIENCE VALIDATION ───────────────────────────── */
  (function expCheck() {
    const el = document.getElementById('id_years_experience');
    if (!el) return;
    el.addEventListener('blur', () => {
      const v = parseInt(el.value, 10);
      if (!el.value) return;
      if (isNaN(v) || v < 0 || v > 70) {
        markError(el, 'Años de experiencia inválidos.');
      } else {
        clearError(el);
      }
    });
  })();

  /* ── 7. BIO CHAR COUNTER ────────────────────────────────── */
  (function bioCounter() {
    const el = document.getElementById('id_bio');
    if (!el) return;
    const MAX = 500;
    const counter = document.createElement('div');
    counter.className = 'field-hint';
    counter.style.textAlign = 'right';
    el.closest('.form-group').appendChild(counter);

    function update() {
      const len = el.value.length;
      counter.textContent = `${len} / ${MAX} caracteres`;
      counter.style.color = len > MAX ? 'var(--txt-err)' : 'var(--txt3)';
    }
    el.addEventListener('input', update);
    update();
  })();

  /* ── 8. SUBMIT HANDLER ──────────────────────────────────── */
  if (form) {
    form.addEventListener('submit', handleSubmit);
    form.querySelectorAll('.form-input, .form-select, .form-textarea').forEach(input => {
      input.addEventListener('focus', () => clearError(input));
    });
  }

  async function handleSubmit(e) {
    e.preventDefault();
    if (!validateAll()) return;

    submitBtn.classList.add('loading');
    submitBtn.disabled = true;

    try {
      const fd  = new FormData(form);
      const res = await fetch(form.action, {
        method: 'POST',
        body: fd,
        headers: { 'X-Requested-With': 'XMLHttpRequest' },
      });

      const data = await res.json().catch(() => ({}));

      if (res.ok && data.success) {
        submitBtn.classList.remove('loading');
        submitBtn.style.background = 'linear-gradient(135deg,#1A5A3A,#3DBB77)';
        submitBtn.style.color = '#fff';
        submitBtn.textContent = '✓ ¡Bienvenido Coach!';
        setTimeout(() => { window.location = data.redirect || '/'; }, 700);
      } else {
        submitBtn.classList.remove('loading');
        submitBtn.disabled = false;
        if (data.errors) displayBackendErrors(data.errors);
        else alert('Error al crear la cuenta. Intenta nuevamente.');
      }
    } catch (err) {
      submitBtn.classList.remove('loading');
      submitBtn.disabled = false;
      console.error(err);
      form.removeEventListener('submit', handleSubmit);
      form.submit();
    }
  }

  /* ── 9. VALIDATION ──────────────────────────────────────── */
  function validateAll() {
    let ok = true;
    form.querySelectorAll('[required]').forEach(input => {
      if (!input.value || (input.type === 'checkbox' && !input.checked)) {
        if (input.type === 'checkbox') {
          const label = input.closest('.form-check');
          if (label) label.style.color = 'var(--txt-err)';
        } else {
          markError(input, 'Este campo es obligatorio.');
        }
        ok = false;
      }
    });

    const email = document.getElementById('id_email');
    if (email && email.value && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.value)) {
      markError(email, 'Email inválido.');
      ok = false;
    }

    const p1 = document.getElementById('id_password1');
    const p2 = document.getElementById('id_password2');
    if (p1 && p2 && p1.value !== p2.value) {
      markError(p2, 'Las contraseñas no coinciden.');
      ok = false;
    }

    return ok;
  }

  /* ── 10. HELPERS ────────────────────────────────────────── */
  function markError(input, msg) {
    input.classList.add('error');
    let err = input.closest('.form-group')?.querySelector('.field-error');
    if (!err) {
      err = document.createElement('div');
      err.className = 'field-error';
      (input.closest('.input-wrap') || input).after(err);
    }
    err.textContent = msg;
  }

  function clearError(input) {
    input.classList.remove('error');
    const err = input.closest('.form-group')?.querySelector('.field-error');
    if (err) err.remove();
  }

  function displayBackendErrors(errors) {
    Object.entries(errors).forEach(([field, msgs]) => {
      const input = document.getElementById(`id_${field}`);
      const msg   = Array.isArray(msgs) ? msgs.join(' ') : msgs;
      if (input) markError(input, msg);
    });
    const firstErr = form.querySelector('.error');
    if (firstErr) firstErr.focus();
  }

  function getCSRF() {
    const token = document.querySelector('[name=csrfmiddlewaretoken]');
    return token ? token.value : '';
  }

  /* Auto-dismiss messages */
  document.querySelectorAll('.msg-item').forEach((m, i) => {
    setTimeout(() => {
      m.style.transition = 'opacity .4s, transform .4s';
      m.style.opacity = '0';
      m.style.transform = 'translateY(-6px)';
      setTimeout(() => m.remove(), 400);
    }, 4500 + i * 400);
  });
})();
