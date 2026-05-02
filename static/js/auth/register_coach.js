/* ═══════════════════════════════════════════════════════════
   REGISTER COACH — Page-specific JS
═══════════════════════════════════════════════════════════ */
(function () {
  'use strict';

  document.addEventListener('DOMContentLoaded', () => {

    const form = document.getElementById('coach-form');
    if (!form) return;

    /* Init shared utilities */
    AuthBase.initEmbers();
    AuthBase.initPasswordToggle();
    AuthBase.initPasswordStrength('id_password1');
    AuthBase.initPasswordMatch();
    AuthBase.initEmailCheck(form, 'register');
    AuthBase.initClearOnFocus(form);
    AuthBase.initAutoDismissMessages();

    /* Years experience validation */
    const yearsEl = document.getElementById('id_years_experience');
    if (yearsEl) {
      yearsEl.addEventListener('blur', () => {
        if (!yearsEl.value) return;
        const v = parseInt(yearsEl.value, 10);
        if (isNaN(v) || v < 0 || v > 70) {
          AuthBase.markError(yearsEl, 'Años de experiencia inválidos (0-70).');
        } else {
          AuthBase.clearError(yearsEl);
        }
      });
    }

    /* Bio character counter */
    const bio = document.getElementById('id_bio');
    if (bio) {
      const MAX = 500;
      const counter = document.createElement('div');
      counter.className = 'field-hint';
      counter.style.textAlign = 'right';
      bio.closest('.form-group').appendChild(counter);

      function update() {
        const len = bio.value.length;
        counter.textContent = `${len} / ${MAX} caracteres`;
        counter.style.color = len > MAX
          ? 'var(--txt-err)'
          : len > MAX * 0.85
            ? 'var(--gold-lo)'
            : 'var(--txt3)';
      }
      bio.addEventListener('input', update);
      update();
    }

    /* Phone format helper */
    const phone = document.getElementById('id_phone');
    if (phone) {
      phone.addEventListener('input', () => {
        /* Allow only +, digits, spaces, parens */
        phone.value = phone.value.replace(/[^\d+\s()-]/g, '');
      });
    }

    /* Form submit */
    form.addEventListener('submit', (e) => {
      e.preventDefault();

      let ok = AuthBase.validateRequired(form);
      ok = AuthBase.validateEmail(form) && ok;
      ok = AuthBase.validatePasswordMatch(form) && ok;
      if (!ok) return;

      AuthBase.submitAjax(form, {
        successText: '⚔ ¡Bienvenido Coach!',
        fallbackUrl: '/',
      });
    });
  });
})();
