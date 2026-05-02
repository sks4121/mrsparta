/* ═══════════════════════════════════════════════════════════
   LOGIN — Page-specific JS
   login.js  |  Depends on auth_base.js
═══════════════════════════════════════════════════════════ */
(function () {
  'use strict';

  document.addEventListener('DOMContentLoaded', () => {

    const form = document.getElementById('login-form');
    if (!form) return;

    /* Init shared utilities */
    AuthBase.initEmbers();
    AuthBase.initPasswordToggle();
    AuthBase.initEmailCheck(form, 'login');
    AuthBase.initClearOnFocus(form);
    AuthBase.initAutoDismissMessages();

    /* Form submit */
    form.addEventListener('submit', async (e) => {
      e.preventDefault();

      /* Frontend validation */
      let ok = AuthBase.validateRequired(form);
      ok = AuthBase.validateEmail(form) && ok;
      if (!ok) return;

      /* AJAX submit with custom success text per role */
      const submitBtn = form.querySelector('.btn-submit');
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

          /* Custom welcome by role */
          const welcome = data.role === 'coach'
            ? '⚔ Bienvenido Coach'
            : data.role === 'athlete'
              ? '🛡 Bienvenido Guerrero'
              : '✓ Acceso concedido';
          submitBtn.textContent = welcome;

          setTimeout(() => {
            window.location = data.redirect || '/';
          }, 700);
        } else {
          submitBtn.classList.remove('loading');
          submitBtn.disabled = false;
          if (data.errors) {
            AuthBase.displayBackendErrors(form, data.errors);
          } else {
            AuthBase.showBanner(form, 'Error al iniciar sesión.', 'error');
          }
        }
      } catch (err) {
        submitBtn.classList.remove('loading');
        submitBtn.disabled = false;
        console.error('Login error:', err);
        form.submit();  /* fallback non-AJAX */
      }
    });

    /* Caps Lock detection on password */
    const pw = document.getElementById('id_password');
    if (pw) {
      let capsLockOn = false;

      function showCapsWarning() {
        let warning = pw.closest('.form-group').querySelector('.caps-warning');
        if (!warning) {
          warning = document.createElement('div');
          warning.className = 'field-hint caps-warning';
          warning.style.cssText = 'color:var(--gold);font-size:11px;';
          warning.textContent = '⚠ Bloq Mayús está activado';
          pw.closest('.input-wrap').after(warning);
        }
        warning.style.display = capsLockOn ? '' : 'none';
      }

      pw.addEventListener('keydown', (e) => {
        if (e.getModifierState) {
          capsLockOn = e.getModifierState('CapsLock');
          showCapsWarning();
        }
      });
      pw.addEventListener('blur', () => {
        const w = pw.closest('.form-group').querySelector('.caps-warning');
        if (w) w.style.display = 'none';
      });
    }
  });
})();
