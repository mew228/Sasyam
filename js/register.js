/**
 * js/register.js
 * ─────────────────────────────────────────────────────────────
 * Sasyam — Farmer Registration + Registry
 * Firebase Firestore SDK v9 (modular, loaded via CDN in HTML)
 * ─────────────────────────────────────────────────────────────
 */

(function () {
  "use strict";

  // ── State ──────────────────────────────────────────────────
  let allFarmers    = [];
  let filteredFarmers = [];
  let currentPage   = 1;
  const PAGE_SIZE   = 15;
  let sortCol       = null;
  let sortDir       = "asc";
  let db            = null;
  let unsubscribe   = null;

  // ── Firebase init ──────────────────────────────────────────
  function initFirebase() {
    const cfg = window.CONFIG?.FIREBASE_CONFIG;
    const fb  = window._firebase;
    if (!cfg?.projectId || !fb) return null;

    try {
      const app  = fb.initializeApp(cfg, "sasyam-register");
      return fb.getFirestore(app);
    } catch (e) {
      console.warn("Firebase init failed:", e.message);
      return null;
    }
  }

  // ── Form Validation ─────────────────────────────────────── //
  const VALIDATORS = {
    name:      v => v.trim().length >= 2          ? "" : "Name must be at least 2 characters.",
    state:     v => v                              ? "" : "Please select a state.",
    district:  v => v.trim().length >= 2          ? "" : "Please enter your district.",
    landSize:  v => parseFloat(v) >= 0.1          ? "" : "Land size must be at least 0.1 acres.",
    primaryCrop:v=> v                              ? "" : "Please select your primary crop.",
    waterSource:v=> v                              ? "" : "Please select a water source.",
    phone:     v => /^[0-9]{10}$/.test(v)         ? "" : "Enter a valid 10-digit mobile number."
  };

  function validateField(name, value) {
    const fn = VALIDATORS[name];
    return fn ? fn(value) : "";
  }

  function showError(fieldId, message) {
    const el = document.getElementById(`err-${fieldId}`);
    const input = document.getElementById(`farmer-${fieldId}`);
    if (el) el.textContent = message;
    if (input) input.classList.toggle("input-error", !!message);
  }

  function clearErrors() {
    Object.keys(VALIDATORS).forEach(k => showError(k, ""));
  }

  function validateForm(data) {
    let valid = true;
    Object.entries(data).forEach(([k, v]) => {
      const err = validateField(k, String(v));
      const fieldId = k === "primaryCrop" ? "crop" : k === "waterSource" ? "water" : k;
      showError(fieldId, err);
      if (err) valid = false;
    });
    return valid;
  }

  // ── Form Submit ────────────────────────────────────────────
  function initForm() {
    const form       = document.getElementById("farmer-form");
    const submitBtn  = document.getElementById("submit-btn");
    const submitText = document.getElementById("submit-text");
    const submitLdr  = document.getElementById("submit-loader");
    const statusBox  = document.getElementById("form-status");

    if (!form) return;

    function setLoading(loading) {
      if (submitBtn)  submitBtn.disabled = loading;
      if (submitText) submitText.hidden  = loading;
      if (submitLdr)  submitLdr.hidden   = !loading;
    }

    function setStatus(msg, type) {
      if (!statusBox) return;
      statusBox.textContent = msg;
      statusBox.className   = `form-status ${type}`;
      statusBox.hidden      = false;
      setTimeout(() => { statusBox.hidden = true; }, 5000);
    }

    form.addEventListener("submit", async e => {
      e.preventDefault();

      const data = {
        name:        form.elements["name"]?.value.trim(),
        state:       form.elements["state"]?.value,
        district:    form.elements["district"]?.value.trim(),
        landSize:    form.elements["landSize"]?.value,
        primaryCrop: form.elements["primaryCrop"]?.value,
        waterSource: form.elements["waterSource"]?.value,
        phone:       form.elements["phone"]?.value.trim()
      };

      clearErrors();
      if (!validateForm(data)) return;

      setLoading(true);

      try {
        const doc = {
          ...data,
          landSize: parseFloat(data.landSize),
          phone: "+91" + data.phone,
          createdAt: db ? window._firebase.serverTimestamp() : new Date().toISOString()
        };

        if (db) {
          const col = window._firebase.collection(db, "farmers");
          await window._firebase.addDoc(col, doc);
        } else {
          // Local demo mode
          allFarmers.unshift({
            ...doc,
            id: "demo-" + Date.now(),
            createdAt: { toDate: () => new Date() }
          });
          renderTable(allFarmers);
          updateBadges(allFarmers.length);
        }

        setStatus("✓ Farm registered successfully! Welcome to Sasyam. 🌾", "success");
        form.reset();

      } catch (err) {
        console.error(err);
        setStatus("Registration failed. Please check your Firebase config and try again.", "error");
      } finally {
        setLoading(false);
      }
    });
  }

  // ── Firestore real-time listener ───────────────────────────
  function subscribeToFarmers() {
    if (!db) {
      // Demo: load empty state
      renderTable([]);
      updateBadges(0);
      const exportBtn = document.getElementById("export-csv");
      if (exportBtn) exportBtn.disabled = true;
      return;
    }

    const { collection, query, orderBy, onSnapshot } = window._firebase;
    const col = collection(db, "farmers");
    const q   = query(col, orderBy("createdAt", "desc"));

    unsubscribe = onSnapshot(q, (snap) => {
      allFarmers = snap.docs.map(doc => ({ id: doc.id, ...doc.data() }));
      filteredFarmers = allFarmers;
      currentPage = 1;
      renderTable(paginate(allFarmers));
      updateBadges(allFarmers.length);
      const exportBtn = document.getElementById("export-csv");
      if (exportBtn) exportBtn.disabled = allFarmers.length === 0;
    }, (err) => {
      console.error("Firestore listener error:", err.message);
    });
  }

  // ── Search ─────────────────────────────────────────────────
  function initSearch() {
    const searchInput = document.getElementById("farmer-search");
    const clearBtn    = document.getElementById("search-clear");
    const badgeFiltered = document.getElementById("badge-filtered");

    if (!searchInput) return;

    searchInput.addEventListener("input", () => {
      const q = searchInput.value.trim().toLowerCase();
      if (clearBtn) clearBtn.hidden = q.length === 0;

      if (!q) {
        filteredFarmers = allFarmers;
        if (badgeFiltered) badgeFiltered.hidden = true;
      } else {
        filteredFarmers = allFarmers.filter(f =>
          [f.name, f.state, f.district, f.primaryCrop, f.waterSource]
            .some(val => (val || "").toLowerCase().includes(q))
        );
        if (badgeFiltered) {
          badgeFiltered.hidden = false;
          document.getElementById("count-filtered").textContent = filteredFarmers.length;
        }
      }

      currentPage = 1;
      renderTable(paginate(filteredFarmers));
    });

    if (clearBtn) {
      clearBtn.addEventListener("click", () => {
        searchInput.value = "";
        searchInput.dispatchEvent(new Event("input"));
      });
    }
  }

  // ── Sorting ────────────────────────────────────────────────
  function initSorting() {
    document.querySelectorAll("th.sortable").forEach(th => {
      th.addEventListener("click", () => {
        const col = th.dataset.col;
        if (sortCol === col) {
          sortDir = sortDir === "asc" ? "desc" : "asc";
        } else {
          sortCol = col;
          sortDir = "asc";
        }

        // Update aria-sort attributes
        document.querySelectorAll("th.sortable").forEach(t => {
          t.setAttribute("aria-sort", "none");
        });
        th.setAttribute("aria-sort", sortDir === "asc" ? "ascending" : "descending");

        filteredFarmers = [...filteredFarmers].sort((a, b) => {
          let va = a[col] ?? "";
          let vb = b[col] ?? "";
          if (typeof va === "number" && typeof vb === "number") {
            return sortDir === "asc" ? va - vb : vb - va;
          }
          va = String(va).toLowerCase();
          vb = String(vb).toLowerCase();
          return sortDir === "asc" ? va.localeCompare(vb) : vb.localeCompare(va);
        });

        currentPage = 1;
        renderTable(paginate(filteredFarmers));
      });
    });
  }

  // ── Pagination ─────────────────────────────────────────────
  function paginate(arr) {
    const start = (currentPage - 1) * PAGE_SIZE;
    return arr.slice(start, start + PAGE_SIZE);
  }

  function initPagination() {
    const prev = document.getElementById("prev-page");
    const next = document.getElementById("next-page");
    if (!prev || !next) return;

    prev.addEventListener("click", () => {
      if (currentPage > 1) { currentPage--; renderTable(paginate(filteredFarmers)); }
    });

    next.addEventListener("click", () => {
      const total = Math.ceil(filteredFarmers.length / PAGE_SIZE);
      if (currentPage < total) { currentPage++; renderTable(paginate(filteredFarmers)); }
    });
  }

  function updatePagination(totalItems) {
    const prev  = document.getElementById("prev-page");
    const next  = document.getElementById("next-page");
    const info  = document.getElementById("page-info");
    const total = Math.ceil(totalItems / PAGE_SIZE) || 1;

    if (prev)  prev.disabled  = currentPage <= 1;
    if (next)  next.disabled  = currentPage >= total;
    if (info)  info.textContent = `Page ${currentPage} of ${total}`;
  }

  // ── Table Render ───────────────────────────────────────────
  function formatDate(ts) {
    if (!ts) return "—";
    const d = ts.toDate ? ts.toDate() : new Date(ts);
    return d.toLocaleDateString("en-IN", { day: "2-digit", month: "short", year: "numeric" });
  }

  function maskPhone(phone) {
    if (!phone || phone.length < 4) return phone;
    return phone.slice(0, -4).replace(/\d/g, "*") + phone.slice(-4);
  }

  function renderTable(farmers) {
    const tbody = document.getElementById("farmer-tbody");
    if (!tbody) return;

    updatePagination(filteredFarmers.length);

    if (!farmers.length) {
      tbody.innerHTML = `
        <tr class="table-empty-row" id="table-placeholder">
          <td colspan="8" class="table-empty">
            <span class="empty-icon">🌱</span>
            <span>${allFarmers.length === 0 ? "No farmers registered yet. Be the first! 🌾" : "No results match your search."}</span>
          </td>
        </tr>
      `;
      return;
    }

    tbody.innerHTML = farmers.map(f => `
      <tr>
        <td>${escapeHtml(f.name || "—")}</td>
        <td>${escapeHtml(f.state || "—")}</td>
        <td>${escapeHtml(f.district || "—")}</td>
        <td>${f.landSize ? Number(f.landSize).toFixed(1) : "—"}</td>
        <td><span class="crop-badge">${escapeHtml(f.primaryCrop || "—")}</span></td>
        <td>${escapeHtml(f.waterSource || "—")}</td>
        <td>${maskPhone(f.phone || "")}</td>
        <td>${formatDate(f.createdAt)}</td>
      </tr>
    `).join("");
  }

  function updateBadges(total) {
    const el = document.getElementById("count-total");
    if (el) el.textContent = total.toLocaleString("en-IN");
  }

  // ── CSV Export ─────────────────────────────────────────────
  function initCsvExport() {
    const btn = document.getElementById("export-csv");
    if (!btn) return;

    btn.addEventListener("click", () => {
      if (!allFarmers.length) return;

      const headers = ["Name", "State", "District", "Land (acres)", "Primary Crop", "Water Source", "Phone", "Registered On"];
      const rows = allFarmers.map(f => [
        f.name, f.state, f.district, f.landSize,
        f.primaryCrop, f.waterSource, f.phone,
        formatDate(f.createdAt)
      ]);

      const csv = [headers, ...rows]
        .map(row => row.map(cell => `"${String(cell ?? "").replace(/"/g, '""')}"`).join(","))
        .join("\n");

      const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
      const url  = URL.createObjectURL(blob);
      const a    = document.createElement("a");
      a.href     = url;
      a.download = `sasyam-farmers-${new Date().toISOString().slice(0,10)}.csv`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    });
  }

  // ── Theme ──────────────────────────────────────────────────
  function initTheme() {
    const saved = localStorage.getItem("sasyam-theme") || "dark";
    document.body.dataset.theme = saved;
  }

  // ── Utilities ──────────────────────────────────────────────
  function escapeHtml(str) {
    const d = document.createElement("div");
    d.textContent = str;
    return d.innerHTML;
  }

  // ── Boot ───────────────────────────────────────────────────
  function init() {
    initTheme();
    db = initFirebase();
    initForm();
    subscribeToFarmers();
    initSearch();
    initSorting();
    initPagination();
    initCsvExport();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }

  // Cleanup
  window.addEventListener("beforeunload", () => {
    if (unsubscribe) unsubscribe();
  });
})();
