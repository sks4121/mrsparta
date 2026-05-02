/* ═══════════════════════════════════════════════
   MR SPARTA COACH — NAVBAR
   navbar.js
═══════════════════════════════════════════════ */

(function () {
  'use strict';

  const navbar    = document.getElementById('navbar');
  const hamburger = document.getElementById('hamburger');
  const mobileMenu = document.getElementById('mobileMenu');

  /* ── Sticky on scroll ── */
  function handleScroll() {
    navbar.classList.toggle('stuck', window.scrollY > 50);
  }
  window.addEventListener('scroll', handleScroll, { passive: true });

  /* ── Hamburger toggle ── */
  function toggleMenu() {
    const isOpen = mobileMenu.classList.toggle('open');
    hamburger.classList.toggle('open', isOpen);
    hamburger.setAttribute('aria-expanded', String(isOpen));
    mobileMenu.setAttribute('aria-hidden', String(!isOpen));
  }

  if (hamburger) {
    hamburger.addEventListener('click', toggleMenu);
  }

  /* ── Close menu on outside click ── */
  document.addEventListener('click', function (e) {
    if (!mobileMenu || !hamburger) return;
    if (!mobileMenu.contains(e.target) && !hamburger.contains(e.target)) {
      mobileMenu.classList.remove('open');
      hamburger.classList.remove('open');
      hamburger.setAttribute('aria-expanded', 'false');
      mobileMenu.setAttribute('aria-hidden', 'true');
    }
  });

  /* ── Close menu on ESC ── */
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && mobileMenu && mobileMenu.classList.contains('open')) {
      mobileMenu.classList.remove('open');
      hamburger.classList.remove('open');
      hamburger.setAttribute('aria-expanded', 'false');
      hamburger.focus();
    }
  });
})();
