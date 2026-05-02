/* ════════════════════════════════════════════════════════════════
   planfitness.js
   Interacciones para las páginas de planes Basic / Premium / Elite
   ════════════════════════════════════════════════════════════════ */
(function () {
    "use strict";

    // ── Helpers ──────────────────────────────────────────────
    const $  = (sel, ctx = document) => ctx.querySelector(sel);
    const $$ = (sel, ctx = document) => Array.from(ctx.querySelectorAll(sel));

    const csrfToken = () => {
        const tag = $('meta[name="csrf-token"]');
        return tag ? tag.content : "";
    };

    /** Toast notifications. */
    const Toast = {
        show(message, type = "ok", duration = 3200) {
            const el = document.createElement("div");
            el.className = `pf-toast pf-toast--${type}`;
            el.textContent = message;
            document.body.appendChild(el);
            // Force reflow so the transition triggers.
            requestAnimationFrame(() => el.classList.add("is-visible"));
            setTimeout(() => {
                el.classList.remove("is-visible");
                setTimeout(() => el.remove(), 400);
            }, duration);
        },
    };

    /** JSON fetch wrapper. */
    async function api(url, { method = "POST", body = null } = {}) {
        const res = await fetch(url, {
            method,
            credentials: "same-origin",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": csrfToken(),
                "X-Requested-With": "XMLHttpRequest",
            },
            body: body ? JSON.stringify(body) : null,
        });
        if (!res.ok) {
            const err = await res.json().catch(() => ({ error: `HTTP ${res.status}` }));
            throw new Error(err.error || "Error en la petición");
        }
        return res.json();
    }

    // ── Acciones de botones ──────────────────────────────────
    const actions = {
        async "generate-plan"(btn) {
            const original = btn.textContent;
            btn.disabled = true;
            btn.textContent = "Generando…";
            try {
                const data = await api("/plans/api/create/");
                Toast.show("¡Plan generado! Redirigiendo…", "ok");
                if (data?.plan?.id) {
                    setTimeout(() => { window.location.href = `/plans/${data.plan.id}/`; }, 800);
                }
            } catch (err) {
                Toast.show(err.message, "error");
                btn.disabled = false;
                btn.textContent = original;
            }
        },

        "show-demo"() {
            Toast.show("Demo próximamente disponible 🎬", "ok");
        },

        "schedule-call"() {
            Toast.show("Te contactaremos en menos de 24h 📞", "ok");
        },
    };

    document.addEventListener("click", (e) => {
        const btn = e.target.closest("[data-action]");
        if (!btn) return;
        const handler = actions[btn.dataset.action];
        if (handler) {
            e.preventDefault();
            handler(btn);
        }
    });

    // ── Counters animados ────────────────────────────────────
    function animateCounter(el) {
        const target = Number(el.dataset.target || 0);
        const duration = 1200;
        const start = performance.now();

        function tick(now) {
            const progress = Math.min((now - start) / duration, 1);
            // easeOutQuart
            const eased = 1 - Math.pow(1 - progress, 4);
            el.textContent = Math.round(target * eased).toLocaleString("es-ES");
            if (progress < 1) requestAnimationFrame(tick);
        }
        requestAnimationFrame(tick);
    }

    const counters = $$("[data-counter]");
    if (counters.length && "IntersectionObserver" in window) {
        const io = new IntersectionObserver((entries) => {
            entries.forEach((entry) => {
                if (entry.isIntersecting) {
                    animateCounter(entry.target);
                    io.unobserve(entry.target);
                }
            });
        }, { threshold: 0.4 });
        counters.forEach((c) => io.observe(c));
    } else {
        counters.forEach(animateCounter);
    }

    // ── Toggle: marcar ejercicio / comida como completado ────
    document.addEventListener("click", async (e) => {
        const checkbox = e.target.closest("[data-toggle]");
        if (!checkbox) return;
        const kind = checkbox.dataset.toggle; // "exercise" | "meal"
        const id   = checkbox.dataset.id;
        if (!id || !["exercise", "meal"].includes(kind)) return;

        try {
            const data = await api(`/plans/api/${kind}/${id}/done/`);
            checkbox.classList.toggle("is-completed", data.completed);
            Toast.show(data.completed ? "¡Marcado como hecho! ✓" : "Desmarcado", "ok", 1800);
        } catch (err) {
            Toast.show(err.message, "error");
        }
    });

    // ── Resaltar nav link activo según ruta ──────────────────
    const path = window.location.pathname;
    $$(".pf-nav-link").forEach((link) => {
        if (link.getAttribute("href") === path) link.classList.add("is-active");
    });

    // ── Log inicial (útil en dev) ────────────────────────────
    if (window?.console?.info) {
        console.info("%c FitnessPro ", "background:#c084fc;color:#0b0d12;font-weight:700;padding:2px 6px;border-radius:4px", "planfitness.js cargado ✓");
    }
})();
