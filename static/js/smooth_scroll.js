/* ═══════════════════════════════════════════════
   MR SPARTA COACH — SMOOTH SCROLL
   smooth_scroll.js
═══════════════════════════════════════════════ */

(function () {
  'use strict';

  document.addEventListener('click', function (e) {
    const link = e.target.closest('a[href^="#"]');
    if (!link) return;

    const href   = link.getAttribute('href');
    if (href === '#') return;

    const target = document.querySelector(href);
    if (!target) return;

    e.preventDefault();

    /* Close mobile menu if open */
    const mobileMenu = document.getElementById('mobileMenu');
    const hamburger  = document.getElementById('hamburger');
    if (mobileMenu) {
      mobileMenu.classList.remove('open');
      mobileMenu.setAttribute('aria-hidden', 'true');
    }
    if (hamburger) {
      hamburger.classList.remove('open');
      hamburger.setAttribute('aria-expanded', 'false');
    }

    target.scrollIntoView({ behavior: 'smooth', block: 'start' });
  });
})();
