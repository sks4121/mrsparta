/* ═══════════════════════════════════════════════
   MR SPARTA COACH — INDEX PAGE JS
   index.js
═══════════════════════════════════════════════ */

(function () {
  'use strict';

  /* ─────────────────────────────────────────────
     ANIMATED STAT COUNTERS
     Triggers when the stats bar enters viewport
  ───────────────────────────────────────────── */

  const statItems = document.querySelectorAll('.stat-val');
  if (!statItems.length) return;

  /**
   * Parse a display string like "500+", "78%", "12K+", "98%"
   * Returns { numeric: number, suffix: string }
   */
  function parseStat(text) {
    const cleaned = text.trim();
    const match   = cleaned.match(/^([\d.]+)([KkMm%+]*)$/);
    if (!match) return { numeric: 0, suffix: cleaned };

    let numeric = parseFloat(match[1]);
    let suffix  = match[2] || '';

    /* Expand K/M so we can count up to it */
    if (suffix.toUpperCase().includes('K')) {
      numeric *= 1000;
      suffix   = suffix.replace(/[Kk]/g, '') + 'K+';
    } else if (suffix.toUpperCase().includes('M')) {
      numeric *= 1000000;
      suffix   = suffix.replace(/[Mm]/g, '') + 'M+';
    }

    return { numeric, suffix };
  }

  /**
   * Format a number back to display form (e.g. 12000 → "12K+")
   */
  function formatStat(value, suffix) {
    if (suffix.includes('K')) {
      return Math.round(value / 1000) + suffix;
    }
    return Math.round(value) + suffix;
  }

  /**
   * Animate a single counter element
   */
  function animateCounter(el, target, suffix, duration) {
    const start     = performance.now();
    const startVal  = 0;

    function step(now) {
      const elapsed  = now - start;
      const progress = Math.min(elapsed / duration, 1);
      /* Ease-out cubic */
      const eased    = 1 - Math.pow(1 - progress, 3);
      const current  = startVal + (target - startVal) * eased;

      el.textContent = formatStat(current, suffix);

      if (progress < 1) {
        requestAnimationFrame(step);
      } else {
        el.textContent = formatStat(target, suffix);
      }
    }

    requestAnimationFrame(step);
  }

  /* Observe stats bar — fire counters once visible */
  const statsBar = document.querySelector('.stats-bar');
  if (!statsBar) return;

  let counted = false;

  const statsObserver = new IntersectionObserver(
    function (entries) {
      if (entries[0].isIntersecting && !counted) {
        counted = true;

        statItems.forEach(function (el) {
          const original        = el.dataset.original || el.textContent;
          el.dataset.original   = original;           /* preserve for re-use */
          const { numeric, suffix } = parseStat(original);
          animateCounter(el, numeric, suffix, 1800);
        });

        statsObserver.disconnect();
      }
    },
    { threshold: 0.4 }
  );

  statsObserver.observe(statsBar);
})();
