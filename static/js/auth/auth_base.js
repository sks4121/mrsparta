/* ═══════════════════════════════════════════════════════════
   AUTH — BASE SHARED JS
   auth_base.js  |  Utilities used across login/register/reset
═══════════════════════════════════════════════════════════ */
'use strict';

/* ═══════════════════════════════════════════════════════════
   1. EMBERS — Particle decoration
═══════════════════════════════════════════════════════════ */
window.AuthBase = window.AuthBase || {};

window.AuthBase.initEmbers = function (count = 22) {
  const container = document.getElementById('embers');
  if (!container) return;

  const frag = document.createDocumentFragment();
  for (let i = 0; i < count; i++) {
    const el = document.createElement('div');
    el.className = 'ember';
    const size = Math.random() * 2.5 + 0.8;
    el.style.cssText = `
      left: ${Math.random() * 100}%;
      bottom: 0;
      width: ${size}px;
      height: ${size}px;
      animation-duration: ${Math.random() * 9 + 6}s;
      animation-delay: ${Math.random() * 14}s;
      --dx: ${(Math.random() - 0.5) * 120}px;
    `;
    frag.appendChild(el);
  }
  container.appendChild(frag);
};

/* ═══════════════════════════════════════════════════════════
   2. PASSWORD VISIBILITY TOGGLE
═══════════════════════════════════════════════════════════ */
window.AuthBase.initPasswordToggle = function () {
  document.querySelectorAll('.input-toggle[data-target]').forEach(btn => {
    btn.addEventListener('click', () => {
      const input = document.getElementById(btn.dataset.target);
      if (!input) return;
      const isText = input.type === 'text';
      input.type = isText ? 'password' : 'text';
      btn.textContent = isText ? '👁' : '🙈';
    });
  });
};

/* ═══════════════════════════════════════════════════════════
   3. PASSWORD STRENGTH METER
═══════════════════════════════════════════════════════════ */
window.AuthBase.initPasswordStrength = function (inputId = 'id_password1') {
  const input = document.getElementById(inputId);
  const bars  = document.querySelectorAll('.pw-bar');
  const label = document.querySelector('.pw-label');
  if (!input || !bars.length) return;

  const LEVELS = [
    { max: 1, cls: 'weak',   txt: 'Débil',  color: '#FF6B6B' },
    { max: 3, cls: 'medium', txt: 'Media',  color: '#C9A84C' },
    { max: 5, cls: 'strong', txt: 'Fuerte', color: '#3DBB77' },
  ];

  function score(pw) {
    let s = 0;
    if (pw.length >= 8)          s++;
    if (pw.length >= 12)         s++;
    if (/[A-Z]/.test(pw))        s++;
    if (/[0-9]/.test(pw))        s++;
    if (/[^A-Za-z0-9]/.test(pw)) s++;
    return s;
  }

  input.addEventListener('input', () => {
    const sc     = score(input.value);
    const level  = LEVELS.find(l => sc <= l.max) || LEVELS[2];
    const filled = sc === 0 ? 0 : sc <= 1 ? 1 : sc <= 3 ? 2 : 3;

    bars.forEach((bar, i) => {
      bar.className = 'pw-bar';
      if (i < filled) bar.classList.add(level.cls);
    });

    if (label) {
      label.textContent = input.value ? level.txt : '';
      label.style.color = level.color;
    }
  });
};

/* ═══════════════════════════════════════════════════════════
   4. PASSWORD CONFIRMATION
═══════════════════════════════════════════════════════════ */
window.AuthBase.initPasswordMatch = function () {
  const p1 = document.getElementById('id_password1');
  const p2 = document.getElementById('id_password2');
  if (!p1 || !p2) return;

  p2.addEventListener('blur', () => {
    if (p2.value && p1.value !== p2.value) {
      window.AuthBase.markError(p2, 'Las contraseñas no coinciden.');
    } else if (p2.value) {
      window.AuthBase.clearError(p2);
    }
  });
};

/* ═══════════════════════════════════════════════════════════
   5. EMAIL LIVE VALIDATION (AJAX)
═══════════════════════════════════════════════════════════ */
window.AuthBase.initEmailCheck = function (form, mode = 'register') {
  // mode = 'register' → email NO debe existir
  // mode = 'login'    → email SÍ debe existir (opcional)
  const input = document.getElementById('id_email');
  if (!input || !form) return;

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
    const ind = getIndicator();
    ind.textContent = '';
    ind.className = 'email-status';

    if (!email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) return;

    timeout = setTimeout(() => {
      ind.className = 'email-status check';
      ind.textContent = '⟳';

      const url = mode === 'register'
        ? form.dataset.checkEmailUrl
        : form.dataset.checkExistsUrl;
      if (!url) return;

      const fd = new FormData();
      fd.append('email', email);
      fd.append('csrfmiddlewaretoken', window.AuthBase.getCSRF());

      fetch(url, { method: 'POST', body: fd })
        .then(r => r.json())
        .then(data => {
          if (mode === 'register') {
            if (data.available) {
              ind.className = 'email-status ok';
              ind.textContent = '✓';
              window.AuthBase.clearError(input);
            } else {
              ind.className = 'email-status err';
              ind.textContent = '✗';
              window.AuthBase.markError(input, data.message || 'Email ya registrado.');
            }
          } else {
            // login mode - just visual feedback
            ind.className = data.exists ? 'email-status ok' : 'email-status';
            ind.textContent = data.exists ? '✓' : '';
          }
        })
        .catch(() => { ind.textContent = ''; });
    }, 500);
  });
};

/* ═══════════════════════════════════════════════════════════
   6. ERROR HELPERS
═══════════════════════════════════════════════════════════ */
window.AuthBase.markError = function (input, msg) {
  input.classList.add('error');
  let err = input.closest('.form-group')?.querySelector('.field-error');
  if (!err) {
    err = document.createElement('div');
    err.className = 'field-error';
    (input.closest('.input-wrap') || input).after(err);
  }
  err.textContent = msg;
};

window.AuthBase.clearError = function (input) {
  input.classList.remove('error');
  const err = input.closest('.form-group')?.querySelector('.field-error');
  if (err) err.remove();
};

window.AuthBase.displayBackendErrors = function (form, errors) {
  Object.entries(errors).forEach(([field, msgs]) => {
    if (field === '__all__') {
      const msg = Array.isArray(msgs) ? msgs.join(' ') : msgs;
      window.AuthBase.showBanner(form, msg, 'error');
      return;
    }
    const input = document.getElementById(`id_${field}`);
    const msg = Array.isArray(msgs) ? msgs.join(' ') : msgs;
    if (input) window.AuthBase.markError(input, msg);
  });
  const firstErr = form.querySelector('.error');
  if (firstErr) firstErr.focus();
};

window.AuthBase.showBanner = function (form, message, type = 'info') {
  let banner = form.querySelector('.msg-item.banner');
  if (!banner) {
    banner = document.createElement('div');
    banner.className = `msg-item banner ${type}`;
    form.insertBefore(banner, form.firstChild);
  }
  banner.textContent = message;
  banner.className = `msg-item banner ${type}`;
};

/* ═══════════════════════════════════════════════════════════
   7. CSRF TOKEN
═══════════════════════════════════════════════════════════ */
window.AuthBase.getCSRF = function () {
  const token = document.querySelector('[name=csrfmiddlewaretoken]');
  return token ? token.value : '';
};

/* ═══════════════════════════════════════════════════════════
   8. AUTO-DISMISS DJANGO MESSAGES
═══════════════════════════════════════════════════════════ */
window.AuthBase.initAutoDismissMessages = function () {
  document.querySelectorAll('.msg-item:not(.banner)').forEach((m, i) => {
    setTimeout(() => {
      m.style.transition = 'opacity .4s, transform .4s';
      m.style.opacity = '0';
      m.style.transform = 'translateY(-6px)';
      setTimeout(() => m.remove(), 400);
    }, 4500 + i * 400);
  });
};

/* ═══════════════════════════════════════════════════════════
   9. CLEAR ERRORS ON FOCUS
═══════════════════════════════════════════════════════════ */
window.AuthBase.initClearOnFocus = function (form) {
  if (!form) return;
  form.querySelectorAll('.form-input, .form-select, .form-textarea').forEach(input => {
    input.addEventListener('focus', () => window.AuthBase.clearError(input));
  });
};

/* ═══════════════════════════════════════════════════════════
   10. FORM VALIDATION HELPERS
═══════════════════════════════════════════════════════════ */
window.AuthBase.validateRequired = function (form) {
  let ok = true;
  form.querySelectorAll('[required]').forEach(input => {
    if (input.type === 'checkbox') {
      if (!input.checked) {
        const label = input.closest('.form-check');
        if (label) label.style.color = 'var(--txt-err)';
        ok = false;
      }
    } else if (!input.value.trim()) {
      window.AuthBase.markError(input, 'Este campo es obligatorio.');
      ok = false;
    }
  });
  return ok;
};

window.AuthBase.validateEmail = function (form) {
  const email = form.querySelector('input[type="email"]');
  if (email && email.value && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.value)) {
    window.AuthBase.markError(email, 'Email inválido.');
    return false;
  }
  return true;
};

window.AuthBase.validatePasswordMatch = function (form) {
  const p1 = document.getElementById('id_password1');
  const p2 = document.getElementById('id_password2');
  if (p1 && p2 && p1.value !== p2.value) {
    window.AuthBase.markError(p2, 'Las contraseñas no coinciden.');
    return false;
  }
  return true;
};

/* ═══════════════════════════════════════════════════════════
   11. AJAX SUBMIT WRAPPER
═══════════════════════════════════════════════════════════ */
window.AuthBase.submitAjax = async function (form, options = {}) {
  const submitBtn = form.querySelector('.btn-submit');
  if (!submitBtn) return;

  submitBtn.classList.add('loading');
  submitBtn.disabled = true;

  try {
    const fd = new FormData(form);
    const res = await fetch(form.action, {
      method: 'POST',
      body: fd,
      headers: { 'X-Requested-With': 'XMLHttpRequest' },
    });

    const data = await res.json().catch(() => ({}));

    if (res.ok && data.success) {
      submitBtn.classList.remove('loading');
      submitBtn.classList.add('success');
      submitBtn.textContent = options.successText || '✓ ¡Listo!';
      setTimeout(() => {
        window.location = data.redirect || options.fallbackUrl || '/';
      }, 700);
    } else {
      submitBtn.classList.remove('loading');
      submitBtn.disabled = false;
      if (data.errors) {
        window.AuthBase.displayBackendErrors(form, data.errors);
      } else {
        window.AuthBase.showBanner(form, 'Error inesperado. Intenta nuevamente.', 'error');
      }
    }
  } catch (err) {
    submitBtn.classList.remove('loading');
    submitBtn.disabled = false;
    console.error('Auth submit error:', err);
    // Fallback to normal submit
    form.submit();
  }
};
