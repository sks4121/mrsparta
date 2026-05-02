/* ═══════════════════════════════════════════════════════════
   REGISTER ATHLETE — Page-specific JS
═══════════════════════════════════════════════════════════ */
(function () {
  'use strict';

  document.addEventListener('DOMContentLoaded', () => {

    const form = document.getElementById('athlete-form');
    if (!form) return;

    /* Init shared utilities */
    AuthBase.initEmbers();
    AuthBase.initPasswordToggle();
    AuthBase.initPasswordStrength('id_password1');
    AuthBase.initPasswordMatch();
    AuthBase.initEmailCheck(form, 'register');
    AuthBase.initClearOnFocus(form);
    AuthBase.initAutoDismissMessages();

    /* Numeric range validation */
    const ranges = [
      { id: 'id_age',       min: 13,   max: 100,  label: 'Edad' },
      { id: 'id_weight_kg', min: 30,   max: 300,  label: 'Peso (kg)' },
      { id: 'id_height_cm', min: 100,  max: 250,  label: 'Altura (cm)' },
    ];
    ranges.forEach(({ id, min, max, label }) => {
      const el = document.getElementById(id);
      if (!el) return;
      el.addEventListener('blur', () => {
        if (!el.value) return;
        const v = parseFloat(el.value);
        if (isNaN(v) || v < min || v > max) {
          AuthBase.markError(el, `${label} debe estar entre ${min} y ${max}.`);
        } else {
          AuthBase.clearError(el);
        }
      });
    });

    /* Form submit */
    form.addEventListener('submit', (e) => {
      e.preventDefault();

      let ok = AuthBase.validateRequired(form);
      ok = AuthBase.validateEmail(form) && ok;
      ok = AuthBase.validatePasswordMatch(form) && ok;
      if (!ok) return;

      AuthBase.submitAjax(form, {
        successText: '✓ ¡Bienvenido guerrero!',
        fallbackUrl: '/',
      });
    });
  });
})();
