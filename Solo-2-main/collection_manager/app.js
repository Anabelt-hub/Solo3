"use strict";

/**
 * Solo Project 3 Frontend
 * ✅ SQL-backed backend
 * ✅ CRUD via fetch()
 * ✅ Paging (configurable) + cookie persistence (pageSize)
 * ✅ Search/filter + Sorting
 * ✅ List view shows images with placeholder
 * ✅ Stats shows: total records + current page size + domain stat
 */

const API_BASE = "https://solo3.onrender.com"; // <-- CHANGE THIS

const el = (id) => document.getElementById(id);

/* --------------------------- Cookie helpers --------------------------- */
function setCookie(name, value, days = 365) {
  const maxAge = days * 24 * 60 * 60;
  document.cookie = `${encodeURIComponent(name)}=${encodeURIComponent(String(value))}; max-age=${maxAge}; path=/; samesite=lax`;
}
function getCookie(name) {
  const key = encodeURIComponent(name) + "=";
  const parts = document.cookie.split(";").map(s => s.trim());
  for (const p of parts) {
    if (p.startsWith(key)) return decodeURIComponent(p.slice(key.length));
  }
  return null;
}

/* --------------------------- DOM --------------------------- */
// Tabs / views
const tabList = el("tabList");
const tabForm = el("tabForm");
const tabStats = el("tabStats");

const viewList = el("viewList");
const viewForm = el("viewForm");
const viewStats = el("viewStats");

// List controls
const recordsTbody = el("recordsTbody");
const searchInput = el("searchInput");
const statusFilter = el("statusFilter");
const sortSelect = el("sortSelect");
const pageSizeSelect = el("pageSizeSelect");
const newBtn = el("newBtn");

// Pager controls
const prevBtn = el("prevPage");
const nextBtn = el("nextPage");
const pageIndicator = el("pageIndicator");

// Form controls
const recordForm = el("recordForm");
const formTitle = el("formTitle");
const recordId = el("recordId");
const titleInput = el("title");
const typeInput = el("type");
const genreInput = el("genre");
const yearInput = el("year");
const ratingInput = el("rating");
const statusInput = el("status");
const imageUrlInput = el("image_url");
const notesInput = el("notes");
const cancelBtn = el("cancelBtn");
const deleteBtn = el("deleteBtn");
const formError = el("formError");

// Stats controls
const statTotal = el("statTotal");
const statPageSize = el("statPageSize");
const statAvgRating = el("statAvgRating");
const statTopGenre = el("statTopGenre");
const statusBreakdown = el("statusBreakdown");

// State
let currentPage = 1;
let totalPages = 1;
let pageSize = Number(getCookie("pageSize")) || 10;

// Current page items only
let records = [];

/* --------------------------- API Helpers --------------------------- */
async function apiFetch(path, options = {}) {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json", ...(options.headers || {}) },
    ...options,
  });

  const contentType = res.headers.get("content-type") || "";
  const isJson = contentType.includes("application/json");
  const data = isJson ? await res.json().catch(() => null) : await res.text().catch(() => null);

  if (!res.ok) {
    const message =
      (data && typeof data === "object" && data.error)
        ? data.error
        : `Request failed (${res.status})`;
    throw new Error(message);
  }
  return data;
}

function getSortParts() {
  // value like "title:asc"
  const raw = sortSelect.value || "title:asc";
  const [sort, dir] = raw.split(":");
  return { sort, dir: (dir === "desc" ? "desc" : "asc") };
}

async function apiGetRecords({ page, search, status, pageSize }) {
  const { sort, dir } = getSortParts();
  const params = new URLSearchParams({
    page: String(page),
    pageSize: String(pageSize),
    search: search || "",
    status: status || "ALL",
    sort,
    dir
  });
  return apiFetch(`/api/records?${params.toString()}`, { method: "GET" });
}

async function apiCreateRecord(record) {
  return apiFetch("/api/records", { method: "POST", body: JSON.stringify(record) });
}

async function apiUpdateRecord(id, record) {
  return apiFetch(`/api/records/${encodeURIComponent(id)}`, { method: "PUT", body: JSON.stringify(record) });
}

async function apiDeleteRecord(id) {
  return apiFetch(`/api/records/${encodeURIComponent(id)}`, { method: "DELETE" });
}

async function apiGetStats() {
  return apiFetch("/api/stats", { method: "GET" });
}

/* --------------------------- View helpers --------------------------- */
function setActiveTab(active) {
  for (const t of [tabList, tabForm, tabStats]) t.classList.remove("active");
  active.classList.add("active");
}

function showView(which) {
  viewList.classList.add("hidden");
  viewForm.classList.add("hidden");
  viewStats.classList.add("hidden");
  which.classList.remove("hidden");
}

function goList() {
  setActiveTab(tabList);
  showView(viewList);
}

function goForm() {
  setActiveTab(tabForm);
  showView(viewForm);
}

function goStats() {
  setActiveTab(tabStats);
  showView(viewStats);
}

/* --------------------------- Validation --------------------------- */
function validateFormData(data) {
  const errs = [];

  if (!data.title || data.title.trim().length === 0) errs.push("Title is required.");
  if (!data.type) errs.push("Type is required.");
  if (!data.genre || data.genre.trim().length === 0) errs.push("Genre is required.");

  if (!Number.isInteger(data.year)) errs.push("Year must be a whole number.");
  if (data.year < 1900 || data.year > 2100) errs.push("Year must be between 1900 and 2100.");

  if (!data.status) errs.push("Status is required.");

  if (!data.image_url || data.image_url.trim().length === 0) errs.push("Image URL is required.");

  if (data.rating !== null) {
    if (!Number.isInteger(data.rating)) errs.push("Rating must be a whole number.");
    if (data.rating < 1 || data.rating > 10) errs.push("Rating must be between 1 and 10.");
  }

  return errs;
}

/* --------------------------- Rendering --------------------------- */
function escapeHtml(str) {
  return String(str)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function renderList() {
  recordsTbody.innerHTML = "";

  if (!records || records.length === 0) {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td colspan="8" class="muted" style="padding:16px;">
        No records found. Try a different search/filter.
      </td>
    `;
    recordsTbody.appendChild(tr);
    return;
  }

  for (const r of records) {
    const tr = document.createElement("tr");

    const safeImg = escapeHtml(r.image_url || "");
    const safeTitle = escapeHtml(r.title || "Untitled");

    tr.innerHTML = `
      <td>
        <img
          class="thumb"
          src="${safeImg}"
          alt="${safeTitle}"
          loading="lazy"
          onerror="this.src='https://via.placeholder.com/84x120?text=No+Image'; this.onerror=null;"
        />
      </td>
      <td>${safeTitle}</td>
      <td>${escapeHtml(r.type)}</td>
      <td>${escapeHtml(r.genre)}</td>
      <td>${r.year}</td>
      <td>${r.rating ?? "—"}</td>
      <td>${escapeHtml(r.status)}</td>
      <td class="right">
        <button data-action="edit" data-id="${r.id}">Edit</button>
        <button data-action="delete" data-id="${r.id}" class="danger">Delete</button>
      </td>
    `;
    recordsTbody.appendChild(tr);
  }
}

function renderPager() {
  pageIndicator.textContent = `Page ${currentPage} of ${totalPages}`;
  prevBtn.disabled = currentPage <= 1;
  nextBtn.disabled = currentPage >= totalPages;
}

/* --------------------------- Stats --------------------------- */
async function refreshStats() {
  const stats = await apiGetStats();

  statTotal.textContent = String(stats.totalRecords ?? "—");
  statPageSize.textContent = String(pageSize);

  statAvgRating.textContent =
    (stats.avgRatingCompleted === null || stats.avgRatingCompleted === undefined)
      ? "—"
      : String(stats.avgRatingCompleted);

  statTopGenre.textContent = stats.topGenre ? String(stats.topGenre) : "—";

  statusBreakdown.innerHTML = "";
  const byStatus = stats.byStatus || {};
  for (const s of ["Planned", "Watching", "Completed", "Dropped"]) {
    const li = document.createElement("li");
    li.textContent = `${s}: ${byStatus[s] ?? 0}`;
    statusBreakdown.appendChild(li);
  }
}

/* --------------------------- Data refresh --------------------------- */
async function refreshFromServer() {
  const data = await apiGetRecords({
    page: currentPage,
    pageSize,
    search: searchInput.value.trim(),
    status: statusFilter.value,
  });

  records = data.items || [];
  currentPage = data.page || 1;
  totalPages = data.totalPages || 1;

  renderList();
  renderPager();
}

/* --------------------------- Form helpers --------------------------- */
function clearForm() {
  recordId.value = "";
  titleInput.value = "";
  typeInput.value = "";
  genreInput.value = "";
  yearInput.value = "";
  ratingInput.value = "";
  statusInput.value = "";
  imageUrlInput.value = "";
  notesInput.value = "";
  formError.classList.add("hidden");
  formError.textContent = "";
  deleteBtn.classList.add("hidden");
  formTitle.textContent = "Add Record";
}

function fillForm(r) {
  recordId.value = r.id;
  titleInput.value = r.title;
  typeInput.value = r.type;
  genreInput.value = r.genre;
  yearInput.value = r.year;
  ratingInput.value = r.rating ?? "";
  statusInput.value = r.status;
  imageUrlInput.value = r.image_url ?? "";
  notesInput.value = r.notes ?? "";
  deleteBtn.classList.remove("hidden");
  formTitle.textContent = "Edit Record";
}

/* --------------------------- Events --------------------------- */
tabList.addEventListener("click", async () => {
  goList();
  await refreshFromServer();
});

tabForm.addEventListener("click", () => {
  clearForm();
  goForm();
});

tabStats.addEventListener("click", async () => {
  goStats();
  await refreshStats();
});

newBtn.addEventListener("click", () => {
  clearForm();
  goForm();
});

// Search/filter/sort should reset to page 1
searchInput.addEventListener("input", async () => {
  currentPage = 1;
  await refreshFromServer();
});

statusFilter.addEventListener("change", async () => {
  currentPage = 1;
  await refreshFromServer();
});

sortSelect.addEventListener("change", async () => {
  currentPage = 1;
  await refreshFromServer();
});

pageSizeSelect.addEventListener("change", async () => {
  pageSize = Number(pageSizeSelect.value) || 10;
  setCookie("pageSize", pageSize, 365);
  currentPage = 1;
  await refreshFromServer();
  await refreshStats();
});

// Pager
prevBtn.addEventListener("click", async () => {
  if (currentPage > 1) {
    currentPage--;
    await refreshFromServer();
  }
});

nextBtn.addEventListener("click", async () => {
  if (currentPage < totalPages) {
    currentPage++;
    await refreshFromServer();
  }
});

// Table actions (edit/delete)
recordsTbody.addEventListener("click", async (e) => {
  const btn = e.target.closest("button");
  if (!btn) return;

  const id = btn.dataset.id;
  const action = btn.dataset.action;
  const rec = records.find((r) => r.id === id);

  if (action === "edit" && rec) {
    fillForm(rec);
    goForm();
  }

  if (action === "delete") {
    const ok = confirm(`Delete "${rec?.title ?? "this record"}"? This cannot be undone.`);
    if (!ok) return;

    try {
      await apiDeleteRecord(id);

      await refreshFromServer();
      if (records.length === 0 && currentPage > 1) {
        currentPage--;
        await refreshFromServer();
      }

      await refreshStats();
    } catch (err) {
      alert(err.message);
    }
  }
});

// Form submit (add/edit)
recordForm.addEventListener("submit", async (e) => {
  e.preventDefault();

  const data = {
    title: titleInput.value.trim(),
    type: typeInput.value,
    genre: genreInput.value.trim(),
    year: Number.parseInt(yearInput.value, 10),
    rating: ratingInput.value.trim() === "" ? null : Number.parseInt(ratingInput.value, 10),
    status: statusInput.value,
    image_url: imageUrlInput.value.trim(),
    notes: notesInput.value.trim(),
  };

  const errs = validateFormData(data);
  if (errs.length > 0) {
    formError.textContent = errs.join(" ");
    formError.classList.remove("hidden");
    return;
  }

  const id = recordId.value;

  try {
    if (id) {
      await apiUpdateRecord(id, data);
    } else {
      await apiCreateRecord(data);
      currentPage = 1; // show newest in first page (depends on backend sort)
    }

    await refreshFromServer();
    await refreshStats();
    goList();
  } catch (err) {
    formError.textContent = err.message;
    formError.classList.remove("hidden");
  }
});

cancelBtn.addEventListener("click", () => goList());

deleteBtn.addEventListener("click", async () => {
  const id = recordId.value;
  if (!id) return;

  const ok = confirm(`Delete this record? This cannot be undone.`);
  if (!ok) return;

  try {
    await apiDeleteRecord(id);

    await refreshFromServer();
    if (records.length === 0 && currentPage > 1) {
      currentPage--;
      await refreshFromServer();
    }

    await refreshStats();
    goList();
  } catch (err) {
    alert(err.message);
  }
});

/* --------------------------- Init --------------------------- */
async function init() {
  try {
    // initialize page size select from cookie
    pageSizeSelect.value = String(pageSize);

    goList();
    await refreshFromServer();
    await refreshStats();
  } catch (err) {
    console.error(err);
    alert(
      `Could not load from server.\n\n` +
      `Check API_BASE in app.js and confirm your backend is running.\n\n` +
      `Error: ${err.message}`
    );
  }
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", init);
} else {
  init();
}

