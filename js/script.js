/**
 * js/script.js
 * ─────────────────────────────────────────────────────────────
 * Sasyam — Landing page interactions
 * · GSAP ScrollTrigger animations (feature cards, hero parallax,
 *   section reveals)
 * · Navigation active-state on scroll
 * · Theme toggle (View Transitions API + class fallback)
 * · Hamburger mobile menu
 * · Contact form handler (placeholder)
 * ─────────────────────────────────────────────────────────────
 */

(function () {
  "use strict";

  // ── Wait for GSAP ────────────────────────────────────────── //
  function waitForGSAP(cb) {
    if (window.gsap && window.ScrollTrigger) {
      cb();
    } else {
      const t = setInterval(() => {
        if (window.gsap && window.ScrollTrigger) {
          clearInterval(t);
          cb();
        }
      }, 50);
    }
  }

  // ── GSAP Animations ──────────────────────────────────────── //
  function initAnimations() {
    gsap.registerPlugin(ScrollTrigger);

    // Hero text parallax
    gsap.to("#hero-title", {
      yPercent: -20,
      ease: "none",
      scrollTrigger: {
        trigger: "#hero",
        start: "top top",
        end: "bottom top",
        scrub: 1.2
      }
    });

    gsap.to("#hero-tagline, #hero-desc, #hero-badge", {
      yPercent: -12,
      opacity: 0.7,
      ease: "none",
      scrollTrigger: {
        trigger: "#hero",
        start: "30% top",
        end: "bottom top",
        scrub: 1.5
      }
    });

    // Feature cards — staggered fade-up
    gsap.utils.toArray(".feature-card").forEach((card, i) => {
      gsap.fromTo(card,
        { opacity: 0, y: 40 },
        {
          opacity: 1,
          y: 0,
          duration: 0.7,
          ease: "power3.out",
          delay: i * 0.08,
          scrollTrigger: {
            trigger: card,
            start: "top 88%",
            toggleActions: "play none none none"
          }
        }
      );
    });

    // Tech layers
    gsap.utils.toArray(".tech-layer").forEach((el, i) => {
      const xFrom = i === 0 ? -30 : i === 2 ? 30 : 0;
      const yFrom = i === 1 ? 30 : 0;
      gsap.fromTo(el,
        { opacity: 0, x: xFrom, y: yFrom },
        {
          opacity: 1, x: 0, y: 0,
          duration: 0.65,
          ease: "power2.out",
          scrollTrigger: {
            trigger: el,
            start: "top 88%",
            toggleActions: "play none none none"
          }
        }
      );
    });

    // Solution cards
    gsap.utils.toArray(".solution-card").forEach((card, i) => {
      gsap.fromTo(card,
        { opacity: 0, y: 30 },
        {
          opacity: 1, y: 0,
          duration: 0.6,
          ease: "power2.out",
          delay: i * 0.1,
          scrollTrigger: {
            trigger: card,
            start: "top 88%",
            toggleActions: "play none none none"
          }
        }
      );
    });

    // Section titles
    gsap.utils.toArray(".section-title, .section-tag").forEach(el => {
      gsap.fromTo(el,
        { opacity: 0, y: 20 },
        {
          opacity: 1, y: 0,
          duration: 0.55,
          ease: "power2.out",
          scrollTrigger: {
            trigger: el,
            start: "top 90%",
            toggleActions: "play none none none"
          }
        }
      );
    });
  }

  // ── Navigation active state on scroll ────────────────────── //
  function initNavActiveState() {
    const sections = document.querySelectorAll("section[id]");
    const navLinks = document.querySelectorAll(".nav-link");

    if (!sections.length || !navLinks.length) return;

    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          const id = entry.target.id;
          navLinks.forEach(link => {
            link.classList.remove("active");
            if (link.getAttribute("href") === `#${id}`) {
              link.classList.add("active");
            }
          });
        }
      });
    }, {
      rootMargin: `-${56 + 20}px 0px -50% 0px`,
      threshold: 0
    });

    sections.forEach(sec => observer.observe(sec));
  }

  // ── Scrolled nav class ────────────────────────────────────  //
  function initScrolledNav() {
    const nav = document.getElementById("main-nav");
    if (!nav) return;
    const onScroll = () => nav.classList.toggle("scrolled", window.scrollY > 20);
    window.addEventListener("scroll", onScroll, { passive: true });
    onScroll();
  }

  // ── Theme Toggle ──────────────────────────────────────────  //
  function initTheme() {
    const btn  = document.getElementById("theme-toggle");
    const body = document.body;
    if (!btn) return;

    // Restore saved preference
    const saved = localStorage.getItem("sasyam-theme") || "dark";
    body.dataset.theme = saved;
    btn.querySelector(".theme-icon").textContent = saved === "dark" ? "☀" : "☾";

    btn.addEventListener("click", () => {
      const next = body.dataset.theme === "dark" ? "light" : "dark";

      // Use View Transitions API if available
      if (document.startViewTransition) {
        document.startViewTransition(() => {
          body.dataset.theme = next;
        });
      } else {
        body.dataset.theme = next;
      }

      localStorage.setItem("sasyam-theme", next);
      btn.querySelector(".theme-icon").textContent = next === "dark" ? "☀" : "☾";
    });
  }

  // ── Hamburger / Mobile Menu ───────────────────────────────  //
  function initHamburger() {
    const hamburger  = document.getElementById("hamburger");
    const mobileMenu = document.getElementById("mobile-menu");
    if (!hamburger || !mobileMenu) return;

    hamburger.addEventListener("click", () => {
      const open = hamburger.getAttribute("aria-expanded") === "true";
      hamburger.setAttribute("aria-expanded", String(!open));
      mobileMenu.classList.toggle("open", !open);
      mobileMenu.setAttribute("aria-hidden", String(open));
      // Prevent body scroll when menu open
      document.body.style.overflow = open ? "" : "hidden";
    });

    // Close on link click
    mobileMenu.querySelectorAll("a").forEach(a => {
      a.addEventListener("click", () => {
        hamburger.setAttribute("aria-expanded", "false");
        mobileMenu.classList.remove("open");
        mobileMenu.setAttribute("aria-hidden", "true");
        document.body.style.overflow = "";
      });
    });

    // Close on Escape
    document.addEventListener("keydown", e => {
      if (e.key === "Escape" && mobileMenu.classList.contains("open")) {
        hamburger.click();
      }
    });
  }

  // ── Contact Form ─────────────────────────────────────────── //
  function initContactForm() {
    const form   = document.getElementById("contact-form");
    const status = document.getElementById("contact-status");
    if (!form) return;

    form.addEventListener("submit", async (e) => {
      e.preventDefault();
      const btn = form.querySelector("[type=submit]");
      btn.textContent = "Sending…";
      btn.disabled = true;

      // Simulate network delay (replace with real endpoint)
      await new Promise(r => setTimeout(r, 1200));

      if (status) {
        status.textContent = "Thank you! We'll be in touch soon. 🌾";
        status.style.cssText = "margin-top:12px;padding:12px 16px;background:rgba(49,162,76,0.10);color:#007D1E;border:1px solid rgba(49,162,76,0.25);border-radius:8px;font-size:14px;font-weight:500;";
      }
      form.reset();
      btn.textContent = "Send Message";
      btn.disabled = false;
    });
  }

  // ── Boot ──────────────────────────────────────────────────  //
  function boot() {
    initTheme();
    initHamburger();
    initScrolledNav();
    initNavActiveState();
    initContactForm();
    waitForGSAP(initAnimations);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }
})();
