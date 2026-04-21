/**
 * js/flower.js
 * ─────────────────────────────────────────────────────────────
 * Sasyam — Scroll-driven image sequence player
 * Plays 300 WebP frames on #bloom-canvas as user scrolls hero.
 * Frames located at: assets/imageSequence/frame_XXXX.webp
 * ─────────────────────────────────────────────────────────────
 */

(function () {
  "use strict";

  // ── Configuration ────────────────────────────────────────── //
  const TOTAL_FRAMES  = 300;
  const FRAME_PAD     = 4;           // 4-digit zero-padded: 0001
  const FRAME_PREFIX  = "assets/imageSequence/frame_";
  const FRAME_EXT     = ".webp";

  // ── State ─────────────────────────────────────────────────  //
  const frames        = new Array(TOTAL_FRAMES);
  let   loadedCount   = 0;
  let   currentFrame  = 0;
  let   rafId         = null;
  let   canvas, ctx, hero;

  // ── Utilities ────────────────────────────────────────────── //
  function padNum(n, width) {
    return String(n).padStart(width, "0");
  }

  function framePath(index) {
    // index is 0-based; file names are 1-based: frame_0001.webp
    return `${FRAME_PREFIX}${padNum(index + 1, FRAME_PAD)}${FRAME_EXT}`;
  }

  // ── Loading Progress UI ───────────────────────────────────  //
  function createProgressBar() {
    const wrap = document.createElement("div");
    wrap.id = "bloom-loader";
    wrap.style.cssText = `
      position:absolute; inset:0; z-index:3;
      display:flex; flex-direction:column; align-items:center; justify-content:center;
      background:rgba(12,16,12,0.85); backdrop-filter:blur(4px);
      transition:opacity 600ms ease;
    `;
    wrap.innerHTML = `
      <div style="color:rgba(255,255,255,0.7);font-size:13px;font-weight:600;
                  letter-spacing:0.1em;text-transform:uppercase;margin-bottom:14px;">
        Loading sequence…
      </div>
      <div style="width:200px;height:3px;background:rgba(255,255,255,0.12);border-radius:2px;overflow:hidden;">
        <div id="bloom-progress-bar"
             style="height:100%;width:0%;background:#0064E0;transition:width 100ms ease;border-radius:2px;">
        </div>
      </div>
      <div id="bloom-progress-text"
           style="color:rgba(255,255,255,0.4);font-size:11px;margin-top:8px;">0 / 300</div>
    `;
    return wrap;
  }

  function updateProgress(loaded) {
    const bar  = document.getElementById("bloom-progress-bar");
    const text = document.getElementById("bloom-progress-text");
    if (!bar) return;
    const pct = Math.round((loaded / TOTAL_FRAMES) * 100);
    bar.style.width  = pct + "%";
    if (text) text.textContent = `${loaded} / ${TOTAL_FRAMES}`;
  }

  function hideLoader() {
    const loader = document.getElementById("bloom-loader");
    if (!loader) return;
    loader.style.opacity = "0";
    setTimeout(() => loader.remove(), 650);
  }

  // ── Canvas Draw ───────────────────────────────────────────  //
  function drawFrame(index) {
    const img = frames[index];
    if (!img || !img.complete || !ctx) return;
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    // Cover-fit the image inside canvas
    const cw = canvas.width,  ch = canvas.height;
    const iw = img.naturalWidth || img.width;
    const ih = img.naturalHeight || img.height;
    if (!iw || !ih) return;
    const scale = Math.max(cw / iw, ch / ih);
    const dw    = iw * scale;
    const dh    = ih * scale;
    const dx    = (cw - dw) / 2;
    const dy    = (ch - dh) / 2;
    ctx.drawImage(img, dx, dy, dw, dh);
  }

  // ── Resize handler ────────────────────────────────────────  //
  function resizeCanvas() {
    canvas.width  = canvas.offsetWidth  || window.innerWidth;
    canvas.height = canvas.offsetHeight || window.innerHeight;
    drawFrame(currentFrame);
  }

  // ── Scroll handler ────────────────────────────────────────  //
  function onScroll() {
    if (!hero) return;
    const heroTop    = hero.getBoundingClientRect().top;
    const heroHeight = hero.offsetHeight;
    const windowH    = window.innerHeight;

    // progress 0 → 1 as hero scrolls from center-visible to fully exited
    const scrolled   = -heroTop;
    const scrollable = heroHeight - windowH;
    const progress   = Math.min(Math.max(scrolled / Math.max(scrollable, 1), 0), 1);

    const targetFrame = Math.min(
      Math.floor(progress * (TOTAL_FRAMES - 1)),
      TOTAL_FRAMES - 1
    );

    if (targetFrame !== currentFrame) {
      currentFrame = targetFrame;
      if (rafId) cancelAnimationFrame(rafId);
      rafId = requestAnimationFrame(() => drawFrame(currentFrame));
    }
  }

  // ── Preload all frames ────────────────────────────────────  //
  function preloadFrames(onComplete) {
    const batchSize = 10;
    let   nextIndex = 0;

    function loadBatch() {
      const end = Math.min(nextIndex + batchSize, TOTAL_FRAMES);
      for (let i = nextIndex; i < end; i++) {
        (function (idx) {
          const img = new Image();
          img.decoding = "async";
          img.onload = img.onerror = function () {
            frames[idx] = img;
            loadedCount++;
            updateProgress(loadedCount);
            if (loadedCount === TOTAL_FRAMES) {
              onComplete();
            }
          };
          img.src = framePath(idx);
          frames[idx] = img;
        })(i);
      }
      nextIndex = end;
      if (nextIndex < TOTAL_FRAMES) {
        // Stagger batches slightly to avoid saturating HTTP/2
        setTimeout(loadBatch, 80);
      }
    }

    loadBatch();
  }

  // ── Init ──────────────────────────────────────────────────  //
  function init() {
    canvas = document.getElementById("bloom-canvas");
    if (!canvas) return;           // Not on a page with the canvas

    ctx    = canvas.getContext("2d");
    hero   = document.getElementById("hero");

    // Attach loader overlay inside hero
    if (hero) {
      const loader = createProgressBar();
      hero.appendChild(loader);
    }

    // Size canvas
    resizeCanvas();
    window.addEventListener("resize", resizeCanvas, { passive: true });

    // Scroll listener
    window.addEventListener("scroll", onScroll, { passive: true });

    // Preload
    preloadFrames(function () {
      hideLoader();
      drawFrame(0);
    });
  }

  // ── Boot ──────────────────────────────────────────────────  //
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
