/* ═══════════════════════════════════════════════════════════
   PASSWORD RESET — Page-specific JS
═══════════════════════════════════════════════════════════ */
(function () {
  'use strict';

  document.addEventListener('DOMContentLoaded', () => {

    const form = document.getElementById('reset-form');
    if (!form) return;

    AuthBase.initEmbers(15);
    AuthBase.initClearOnFocus(form);
    AuthBase.initAutoDismissMessages();

    form.addEventListener('submit', async (e) => {
      e.preventDefault();

      let ok = AuthBase.validateRequired(form);
      ok = AuthBase.validateEmail(form) && ok;
      if (!ok) return;

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
          /* Show success state */
          const card = form.closest('.reset-card');
          if (card) {
            card.innerHTML = `
              <div class="reset-success">
                <div class="reset-success-icon">✓</div>
                <h2 class="reset-success-title">Email enviado</h2>
                <p class="reset-success-text">
                  ${data.message || 'Si el email existe, recibirás instrucciones en breve. Revisa tu bandeja de entrada y la carpeta de spam.'}
                </p>
                <a href="/auth/login/" class="btn-submit" style="text-decoration:none;display:inline-flex;align-items:center;justify-content:center;padding:12px 28px;width:auto">
                  ← Volver al login
                </a>
              </div>
            `;
          }
        } else {
          submitBtn.classList.remove('loading');
          submitBtn.disabled = false;
          if (data.errors) {
            AuthBase.displayBackendErrors(form, data.errors);
          }
        }
      } catch (err) {
        submitBtn.classList.remove('loading');
        submitBtn.disabled = false;
        console.error(err);
        form.submit();
      }
    });
  });
})();
