/**
 * app.js — PathWise Frontend
 *
 * Architecture: page-function pattern.
 * Each HTML page has a corresponding init function that is
 * called if the page's root element is detected in the DOM.
 *
 * Shared state stored in localStorage:
 *   selectedCareerId  (string | null)  — the career the user is targeting
 *
 * All scoring logic lives in Python (engine.py).
 * JavaScript only fetches JSON from the Flask API and renders it.
 */

'use strict';

/* ============================================================
   Constants
   ============================================================ */

const API = '';  // Same-origin; Flask serves both API and web/

const LEVEL_LABELS = {
  1: 'Beginner',
  2: 'Basic',
  3: 'Intermediate',
  4: 'Advanced',
  5: 'Expert',
};

const CAREER_ICONS = {
  'Business Analyst':   '📊',
  'Data Analyst':       '🔬',
  'Marketing Analyst':  '📣',
  'Financial Analyst':  '💰',
};

const CATEGORY_ORDER = ['Technical', 'Business', 'Soft Skill'];

/* ============================================================
   Shared State Helpers
   ============================================================ */

function getSelectedCareerId() {
  const raw = localStorage.getItem('selectedCareerId');
  return raw ? parseInt(raw, 10) : null;
}

function setSelectedCareerId(id) {
  localStorage.setItem('selectedCareerId', String(id));
}

function getSelectedCareerName() {
  return localStorage.getItem('selectedCareerName') || null;
}

function setSelectedCareerName(name) {
  localStorage.setItem('selectedCareerName', name);
}

/* ============================================================
   API Fetch Wrapper
   ============================================================ */

async function apiFetch(path) {
  const res = await fetch(API + path);
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`HTTP ${res.status}: ${text}`);
  }
  return res.json();
}

/* ============================================================
   Toast Notification System
   ============================================================ */

function showToast(message, type = 'success') {
  const stack = document.getElementById('toast-stack');
  if (!stack) return;

  const icon = type === 'success' ? '✓' : '✗';
  const toast = document.createElement('div');
  toast.className = `toast toast--${type}`;
  toast.innerHTML = `<span class="toast__icon">${icon}</span><span>${message}</span>`;
  stack.appendChild(toast);

  setTimeout(() => {
    toast.classList.add('toast--leaving');
    toast.addEventListener('animationend', () => toast.remove());
  }, 2800);
}

/* ============================================================
   Shared Components
   ============================================================ */

/** Renders a loading spinner into the given container element. */
function renderSpinner(container, message = 'Loading…') {
  container.innerHTML = `
    <div class="spinner-wrap">
      <progress class="spinner" aria-label="${message}"></progress>
      <p>${message}</p>
    </div>`;
}

/** Renders an "empty / no career selected" prompt. */
function renderNoCareer(container) {
  container.innerHTML = `
    <div class="empty-state">
      <div class="empty-state__icon">🎯</div>
      <p class="empty-state__title">No target career selected</p>
      <p class="empty-state__desc">
        Go to <strong>Career Explorer</strong> and choose a target career to see your analysis.
      </p>
      <a href="careers.html" class="btn btn--primary">Choose a Career</a>
    </div>`;
}

/** Renders an error message inside a container. */
function renderError(container, message) {
  container.innerHTML = `
    <div class="empty-state">
      <div class="empty-state__icon">⚠️</div>
      <p class="empty-state__title">Something went wrong</p>
      <p class="empty-state__desc">${message}</p>
    </div>`;
}

/** Progress ring: set value 0-100 and update inner text.
 *  Uses --progress (registered @property) for smooth conic-gradient animation.
 *  Falls back to direct setProperty for browsers without attr() support.
 */
function updateFitRing(ring, content, value) {
  const rounded = Math.round(value);

  // Always keep the <progress> value attribute as semantic source of truth
  ring.setAttribute('value', rounded);

  // Directly drive the conic-gradient via the registered --progress property.
  // For browsers that support attr() in CSS (Chrome 133+, Edge 133+, FF 155+),
  // this is also handled by CSS; we set it here as the universal fallback.
  ring.style.setProperty('--progress', rounded);

  if (content) content.textContent = `${rounded}%`;
}

/** Returns HTML for a level bar given current and max (5). */
function levelBarHTML(level, max = 5) {
  const pct = Math.round((level / max) * 100);
  return `
    <div class="level-bar-wrap">
      <div class="level-bar-track">
        <div class="level-bar-fill" style="width:${pct}%"></div>
      </div>
      <span class="level-num">${level}</span>
    </div>`;
}

/** Returns a badge HTML string based on gap/blocked status. */
function gapBadgeHTML(skill) {
  if (skill.gap === 0) {
    return '<span class="badge badge--success">✓ Met</span>';
  }
  if (skill.is_blocked) {
    const blockers = skill.blocked_by.join(', ');
    return `<span class="badge badge--danger">Blocked by ${blockers}</span>`;
  }
  return `<span class="badge badge--warning">Gap: ${skill.gap}</span>`;
}

/* ============================================================
   Page: Dashboard (index.html)
   ============================================================ */

async function initDashboardPage() {
  const container = document.getElementById('dashboard-content');
  if (!container) return;

  const careerId   = getSelectedCareerId();
  const careerName = getSelectedCareerName();

  if (!careerId) {
    // Show prompt and a small API health check
    container.innerHTML = `
      <div class="empty-state">
        <div class="empty-state__icon">🎯</div>
        <p class="empty-state__title">Welcome to PathWise</p>
        <p class="empty-state__desc">
          Select your target career to see your Career Fit score,<br>
          recommended next skill, and personalized learning roadmap.
        </p>
        <a href="careers.html" class="btn btn--primary">Get Started → Choose a Career</a>
      </div>`;
    return;
  }

  renderSpinner(container, 'Analysing your profile…');

  try {
    const data = await apiFetch(`/api/analysis?career_id=${careerId}`);
    renderDashboard(container, data);
  } catch (err) {
    renderError(container, err.message);
  }
}

function renderDashboard(container, data) {
  const fit   = data.career_fit;
  const rec   = data.recommendation;
  const skills = data.skill_analysis;

  const gapCount = skills.filter(s => s.gap > 0).length;
  const metCount = skills.filter(s => s.gap === 0).length;
  const total    = skills.length;

  container.innerHTML = `
    <!-- Career Fit ring -->
    <div class="fit-display" id="fit-display">
      <div class="fit-ring-wrapper">
        <progress class="fit-ring" id="fit-ring" value="0" max="100" aria-label="Career Fit ${Math.round(fit)}%"></progress>
        <div class="fit-ring-content" id="fit-ring-content">0%</div>
      </div>
      <div class="fit-info">
        <div class="fit-info__career">Target Career</div>
        <div class="fit-info__title">${data.career_name}</div>
        <div class="fit-info__desc">
          Your profile matches <strong>${Math.round(fit)}%</strong> of the requirements for this career.
          ${gapCount > 0
            ? `You have <strong>${gapCount}</strong> skill gap${gapCount !== 1 ? 's' : ''} to close.`
            : 'You meet all skill requirements!'}
        </div>
      </div>
    </div>

    <!-- Stats -->
    <div class="stat-grid">
      <div class="stat-card">
        <div class="stat-card__label">Career Fit</div>
        <div class="stat-card__value stat-card__value--primary">${Math.round(fit)}%</div>
        <div class="stat-card__sub">Weighted skill match</div>
      </div>
      <div class="stat-card">
        <div class="stat-card__label">Skills with Gap</div>
        <div class="stat-card__value stat-card__value--warning">${gapCount}</div>
        <div class="stat-card__sub">of ${total} required</div>
      </div>
      <div class="stat-card">
        <div class="stat-card__label">Skills Met</div>
        <div class="stat-card__value stat-card__value--success">${metCount}</div>
        <div class="stat-card__sub">at or above requirement</div>
      </div>
    </div>

    ${rec ? renderRecCardHTML(rec) : `
      <div class="card mb-4">
        <p class="text-muted">🎉 All required skills are met. No further learning is needed for this career.</p>
      </div>`}

    <!-- Quick navigation -->
    <div class="flex gap-3 mt-4">
      <a href="gap.html" class="btn btn--outline">View Full Skill Gap →</a>
      <a href="roadmap.html" class="btn btn--ghost">See Learning Roadmap</a>
      <a href="careers.html" class="btn btn--ghost">Change Career</a>
    </div>`;

  // Animate progress ring
  requestAnimationFrame(() => {
    setTimeout(() => {
      const ring    = document.getElementById('fit-ring');
      const content = document.getElementById('fit-ring-content');
      if (ring) updateFitRing(ring, content, fit);
    }, 100);
  });
}

function renderRecCardHTML(rec) {
  const exp = rec.explanation || {};
  return `
    <div class="rec-card mb-6">
      <div class="rec-card__eyebrow">⭐ Recommended Next Skill</div>
      <div class="rec-card__skill">${rec.skill_name}</div>
      <div class="rec-card__score">
        Priority Score: <strong>${rec.priority_score}</strong> / 100
        &nbsp;·&nbsp; Gap: ${rec.gap} level${rec.gap !== 1 ? 's' : ''}
        &nbsp;·&nbsp; ${LEVEL_LABELS[rec.current_level] || rec.current_level} → ${LEVEL_LABELS[rec.required_level] || rec.required_level}
      </div>
      <div class="rec-card__breakdown">
        <div class="rec-factor">
          <div class="rec-factor__label">Gap (30%)</div>
          <div class="rec-factor__value">+${exp.gap_contribution ?? '—'}</div>
        </div>
        <div class="rec-factor">
          <div class="rec-factor__label">Importance (30%)</div>
          <div class="rec-factor__value">+${exp.importance_contribution ?? '—'}</div>
        </div>
        <div class="rec-factor">
          <div class="rec-factor__label">Demand (20%)</div>
          <div class="rec-factor__value">+${exp.demand_contribution ?? '—'}</div>
        </div>
        <div class="rec-factor">
          <div class="rec-factor__label">Strategic (20%)</div>
          <div class="rec-factor__value">+${exp.strategic_contribution ?? '—'}</div>
        </div>
      </div>
      ${exp.prerequisite_status
        ? `<div class="rec-card__explanation">📌 ${exp.prerequisite_status}</div>`
        : ''}
    </div>`;
}

/* ============================================================
   Page: My Skills (skills.html)
   ============================================================ */

async function initSkillsPage() {
  const container = document.getElementById('skills-content');
  if (!container) return;

  renderSpinner(container, 'Loading your skills…');

  try {
    const skills = await apiFetch('/api/user/skills');
    renderSkillsEditor(container, skills);
  } catch (err) {
    renderError(container, err.message);
  }
}

function renderSkillsEditor(container, skills) {
  // Group by category in defined order
  const byCategory = {};
  for (const cat of CATEGORY_ORDER) byCategory[cat] = [];
  for (const s of skills) {
    const cat = s.category || 'Other';
    if (!byCategory[cat]) byCategory[cat] = [];
    byCategory[cat].push(s);
  }

  let html = '';
  for (const cat of Object.keys(byCategory)) {
    const group = byCategory[cat];
    if (!group.length) continue;

    const rows = group.map(s => `
      <div class="skill-row" id="skill-row-${s.skill_id}">
        <div class="skill-row__info">
          <div class="skill-row__name">${s.skill_name}</div>
          <div class="skill-row__cat">${s.category}</div>
        </div>
        <div class="skill-row__control">
          <select
            class="level-select"
            id="select-${s.skill_id}"
            aria-label="Level for ${s.skill_name}"
            data-skill-id="${s.skill_id}"
            data-original="${s.current_level}"
          >
            ${[1,2,3,4,5].map(v =>
              `<option value="${v}" ${v === s.current_level ? 'selected' : ''}>${v} — ${LEVEL_LABELS[v]}</option>`
            ).join('')}
          </select>
        </div>
        <div>
          <button
            class="save-btn"
            id="save-btn-${s.skill_id}"
            data-skill-id="${s.skill_id}"
            onclick="saveSkillLevel(${s.skill_id})"
          >Save</button>
        </div>
      </div>`).join('');

    html += `
      <div class="category-section">
        <div class="category-title">${cat}</div>
        <div class="skills-grid">${rows}</div>
      </div>`;
  }

  container.innerHTML = html;
}

async function saveSkillLevel(skillId) {
  const select = document.getElementById(`select-${skillId}`);
  const btn    = document.getElementById(`save-btn-${skillId}`);
  if (!select || !btn) return;

  const level = parseInt(select.value, 10);
  btn.disabled = true;
  btn.textContent = 'Saving…';

  try {
    await fetch(`${API}/api/user/skills`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ skill_id: skillId, current_level: level }),
    }).then(r => {
      if (!r.ok) throw new Error(`HTTP ${r.status}`);
      return r.json();
    });

    select.dataset.original = level;
    btn.textContent = 'Saved ✓';
    setTimeout(() => { btn.textContent = 'Save'; btn.disabled = false; }, 1500);
    showToast('Skill level updated', 'success');
  } catch (err) {
    btn.textContent = 'Error';
    setTimeout(() => { btn.textContent = 'Save'; btn.disabled = false; }, 2000);
    showToast(`Save failed: ${err.message}`, 'error');
  }
}

// Make saveSkillLevel available globally (called from onclick)
window.saveSkillLevel = saveSkillLevel;

/* ============================================================
   Page: Career Explorer (careers.html)
   ============================================================ */

async function initCareersPage() {
  const container = document.getElementById('careers-content');
  if (!container) return;

  renderSpinner(container, 'Loading careers…');

  try {
    const [careers, user] = await Promise.all([
      apiFetch('/api/careers'),
      apiFetch('/api/user/skills'),
    ]);
    renderCareers(container, careers, user);
  } catch (err) {
    renderError(container, err.message);
  }
}

function renderCareers(container, careers, userSkills) {
  const selectedId = getSelectedCareerId();
  const userMap    = Object.fromEntries(userSkills.map(s => [s.skill_id, s.current_level]));

  const cards = careers.map(career => {
    const isSelected = career.career_id === selectedId;
    const icon = CAREER_ICONS[career.career_name] || '💼';

    return `
      <div
        class="card card--interactive ${isSelected ? 'card--selected' : ''}"
        id="career-card-${career.career_id}"
        onclick="selectCareer(${career.career_id}, '${career.career_name.replace(/'/g, "\\'")}')"
        role="button"
        tabindex="0"
        aria-pressed="${isSelected}"
      >
        <div class="career-card__icon">${icon}</div>
        <div class="career-card__name">${career.career_name}</div>
        ${isSelected
          ? '<div class="career-card__badge">✓ Selected</div>'
          : '<div style="height:22px"></div>'}
        <button
          class="btn ${isSelected ? 'btn--selected' : 'btn--primary'}"
          onclick="event.stopPropagation(); selectAndNavigate(${career.career_id}, '${career.career_name.replace(/'/g, "\\'")}')"
        >
          ${isSelected ? '✓ Current Target' : 'Select & Analyse →'}
        </button>
      </div>`;
  }).join('');

  container.innerHTML = `
    <div class="career-grid" id="career-grid">${cards}</div>
    <p class="text-muted mt-6" style="font-size:0.85rem">
      Click a career card to set it as your target. Your skill gap analysis and roadmap will update automatically.
    </p>`;
}

function selectCareer(id, name) {
  setSelectedCareerId(id);
  setSelectedCareerName(name);
  // Re-render cards to update selected state
  document.querySelectorAll('.card--interactive').forEach(c => {
    c.classList.remove('card--selected');
    c.setAttribute('aria-pressed', 'false');
  });
  const card = document.getElementById(`career-card-${id}`);
  if (card) {
    card.classList.add('card--selected');
    card.setAttribute('aria-pressed', 'true');
  }
  showToast(`"${name}" set as your target career`, 'success');
}

function selectAndNavigate(id, name) {
  setSelectedCareerId(id);
  setSelectedCareerName(name);
  window.location.href = 'gap.html';
}

window.selectCareer        = selectCareer;
window.selectAndNavigate   = selectAndNavigate;

/* ============================================================
   Page: Skill Gap (gap.html)
   ============================================================ */

async function initGapPage() {
  const container = document.getElementById('gap-content');
  if (!container) return;

  const careerId = getSelectedCareerId();
  if (!careerId) {
    renderNoCareer(container);
    return;
  }

  renderSpinner(container, 'Calculating skill gaps…');

  try {
    const data = await apiFetch(`/api/analysis?career_id=${careerId}`);
    renderGapPage(container, data);
  } catch (err) {
    renderError(container, err.message);
  }
}

function renderGapPage(container, data) {
  const rec    = data.recommendation;
  const skills = data.skill_analysis;
  const fit    = data.career_fit;

  // Sort: candidates (with gap) first by priority desc, then met skills
  const candidates = skills.filter(s => s.gap > 0).sort((a, b) => b.priority_score - a.priority_score);
  const met        = skills.filter(s => s.gap === 0);

  const tableRows = [...candidates, ...met].map(s => {
    const matchPct = Math.round(s.skill_match);
    return `
      <tr>
        <td>
          <div style="font-weight:600">${s.skill_name}</div>
          <div style="font-size:0.75rem;color:var(--color-text-subtle)">${s.category}</div>
        </td>
        <td>${levelBarHTML(s.current_level)}</td>
        <td>${levelBarHTML(s.required_level)}</td>
        <td style="text-align:center;font-weight:600;color:${s.gap > 0 ? 'var(--color-warning)' : 'var(--color-success)'}">${s.gap}</td>
        <td>${gapBadgeHTML(s)}</td>
        <td style="text-align:right;font-weight:600;font-variant-numeric:tabular-nums">
          ${s.gap > 0 ? s.priority_score : '—'}
        </td>
      </tr>`;
  }).join('');

  container.innerHTML = `
    <!-- Career Fit -->
    <div class="fit-display" id="fit-display">
      <div class="fit-ring-wrapper">
        <progress class="fit-ring" id="fit-ring" value="0" max="100" aria-label="Career Fit ${Math.round(fit)}%"></progress>
        <div class="fit-ring-content" id="fit-ring-content">0%</div>
      </div>
      <div class="fit-info">
        <div class="fit-info__career">Career Fit — ${data.career_name}</div>
        <div class="fit-info__title">${Math.round(fit)}% Match</div>
        <div class="fit-info__desc">
          ${candidates.length} skill gap${candidates.length !== 1 ? 's' : ''} identified.
          ${candidates.filter(s => s.is_blocked).length} blocked by prerequisites.
        </div>
      </div>
    </div>

    <!-- Recommendation -->
    ${rec ? renderRecCardHTML(rec) : `
      <div class="card mb-6">
        <p>🎉 <strong>No skill gaps!</strong> You already meet all requirements for ${data.career_name}.</p>
      </div>`}

    <!-- Full table -->
    <div class="table-wrapper">
      <div class="table-header">
        <span class="table-title">Skill Analysis — ${data.career_name}</span>
        <span class="text-muted" style="font-size:0.8rem">${skills.length} skills</span>
      </div>
      <table>
        <thead>
          <tr>
            <th>Skill</th>
            <th>Your Level</th>
            <th>Required</th>
            <th style="text-align:center">Gap</th>
            <th>Status</th>
            <th style="text-align:right">Priority</th>
          </tr>
        </thead>
        <tbody>${tableRows}</tbody>
      </table>
    </div>

    <div class="flex gap-3 mt-6">
      <a href="roadmap.html" class="btn btn--primary">View Learning Roadmap →</a>
      <a href="skills.html" class="btn btn--ghost">Update My Skills</a>
      <a href="careers.html" class="btn btn--ghost">Change Career</a>
    </div>`;

  // Animate ring
  requestAnimationFrame(() => {
    setTimeout(() => {
      const ring    = document.getElementById('fit-ring');
      const content = document.getElementById('fit-ring-content');
      if (ring) updateFitRing(ring, content, fit);
    }, 100);
  });
}

/* ============================================================
   Page: Learning Roadmap (roadmap.html)
   ============================================================ */

async function initRoadmapPage() {
  const container = document.getElementById('roadmap-content');
  if (!container) return;

  const careerId = getSelectedCareerId();
  if (!careerId) {
    renderNoCareer(container);
    return;
  }

  renderSpinner(container, 'Building your roadmap…');

  try {
    const data = await apiFetch(`/api/roadmap?career_id=${careerId}`);
    renderRoadmapPage(container, data);
  } catch (err) {
    renderError(container, err.message);
  }
}

function renderRoadmapPage(container, data) {
  const steps = data.roadmap;

  if (!steps || steps.length === 0) {
    container.innerHTML = `
      <div class="empty-state">
        <div class="empty-state__icon">🎉</div>
        <p class="empty-state__title">Nothing left to learn!</p>
        <p class="empty-state__desc">
          You already meet all skill requirements for <strong>${data.career_name}</strong>.
        </p>
        <a href="careers.html" class="btn btn--outline">Explore other careers</a>
      </div>`;
    return;
  }

  const stepItems = steps.map((step, i) => {
    const gapPct  = Math.round(step.gap_score);
    const matchPct = Math.round(step.skill_match);
    const blocked  = step.is_blocked;

    return `
      <div class="roadmap-step" id="roadmap-step-${step.skill_id}">
        <div class="roadmap-step__line-col">
          <div class="roadmap-step__num">${i + 1}</div>
          <div class="roadmap-step__connector"></div>
        </div>
        <div class="roadmap-step__body">
          <div class="roadmap-step__name">${step.skill_name}</div>
          <div class="roadmap-step__meta">
            <span class="badge badge--muted">${step.category}</span>
            ${gapBadgeHTML(step)}
            <span class="text-muted" style="font-size:0.8rem">
              Level ${step.current_level} → ${step.required_level}
              (${LEVEL_LABELS[step.current_level] || step.current_level} → ${LEVEL_LABELS[step.required_level] || step.required_level})
            </span>
          </div>
          <div class="roadmap-step__scores">
            <div class="score-item">
              <div class="score-item__label">Priority Score</div>
              <div class="score-item__val" style="color:var(--color-accent)">${step.priority_score}</div>
            </div>
            <div class="score-item">
              <div class="score-item__label">Gap Score</div>
              <div class="score-item__val" style="color:var(--color-warning)">${gapPct}</div>
            </div>
            <div class="score-item">
              <div class="score-item__label">Skill Match</div>
              <div class="score-item__val" style="color:var(--color-success)">${matchPct}%</div>
            </div>
            <div class="score-item">
              <div class="score-item__label">Importance</div>
              <div class="score-item__val">${step.importance}</div>
            </div>
          </div>
          ${(step.blocked_by && step.blocked_by.length > 0)
            ? `<div class="rec-card__explanation mt-2">🔒 Requires: ${step.blocked_by.join(', ')}</div>`
            : ''}
        </div>
      </div>`;
  }).join('');

  container.innerHTML = `
    <div class="card mb-6" style="outline:2px solid var(--color-accent-border);outline-offset:0">
      <div style="font-size:0.68rem;font-weight:700;text-transform:uppercase;letter-spacing:0.12em;color:var(--color-text-dim);margin-bottom:var(--space-2)">
        Target Career
      </div>
      <div style="font-family:var(--font-serif);font-size:1.2rem;font-weight:600;color:var(--color-text)">${data.career_name}</div>
      <div class="text-muted mt-2" style="font-size:0.85rem">
        ${steps.length} skill${steps.length !== 1 ? 's' : ''} to learn, in prerequisite-safe order.
        Ties are broken by Priority Score.
      </div>
    </div>

    <div class="roadmap-list">${stepItems}</div>

    <div class="flex gap-3 mt-6">
      <a href="skills.html" class="btn btn--primary">Update My Skills →</a>
      <a href="gap.html" class="btn btn--ghost">Back to Skill Gap</a>
    </div>`;
}

/* ============================================================
   Router — detect current page and call init function
   ============================================================ */

document.addEventListener('DOMContentLoaded', () => {
  if (document.getElementById('dashboard-content')) initDashboardPage();
  if (document.getElementById('skills-content'))    initSkillsPage();
  if (document.getElementById('careers-content'))   initCareersPage();
  if (document.getElementById('gap-content'))       initGapPage();
  if (document.getElementById('roadmap-content'))   initRoadmapPage();
});
