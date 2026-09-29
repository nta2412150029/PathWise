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
  const introContainer = document.getElementById('dashboard-intro');
  const contentContainer = document.getElementById('dashboard-content');
  if (!introContainer || !contentContainer) return;

  const careerId   = getSelectedCareerId();
  const careerName = getSelectedCareerName();

  if (!careerId) {
    introContainer.innerHTML = `
      <div class="empty-state">
        <p class="empty-state__title" style="margin-top:0;">Welcome to PathWise</p>
        <p class="empty-state__desc">
          Select your target career to see your Career Fit score,<br>
          recommended next skill, and personalized learning roadmap.
        </p>
        <a href="skills.html" class="btn btn--primary">GET STARTED → BUILD YOUR SKILLS</a>
      </div>`;
    contentContainer.innerHTML = '';
    return;
  }

  renderSpinner(introContainer, 'Analysing your profile…');

  try {
    const data = await apiFetch(`/api/analysis?career_id=${careerId}`);
    renderDashboard(introContainer, contentContainer, data);
  } catch (err) {
    renderError(introContainer, err.message);
  }
}

function renderDashboard(introContainer, contentContainer, data) {
  const fit   = data.career_fit;
  const rec   = data.recommendation;
  const skills = data.skill_analysis;

  const gapCount = skills.filter(s => s.gap > 0).length;
  const metCount = skills.filter(s => s.gap === 0).length;
  const total    = skills.length;

  introContainer.innerHTML = `
    <!-- Career Fit ring -->
    <div class="fit-display" id="fit-display" style="border-bottom: none; padding-bottom: 0;">
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
    </div>`;

  contentContainer.innerHTML = `
    <!-- Stats -->
    <div class="stat-grid" style="margin-top: 0;">
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
      <div style="padding: var(--space-8) 0; border-bottom: 1px solid var(--color-border);">
        <p class="text-muted">🎉 All required skills are met. No further learning is needed for this career.</p>
      </div>`}

    <!-- Quick navigation -->
    <div class="flex gap-4" style="padding-top: var(--space-6);">
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
            onchange="checkUnsavedChanges()"
          >
            ${[1,2,3,4,5].map(v =>
              `<option value="${v}" ${v === s.current_level ? 'selected' : ''}>${v} — ${LEVEL_LABELS[v]}</option>`
            ).join('')}
          </select>
        </div>
      </div>`).join('');

    html += `
      <div class="category-section">
        <div class="category-title">${cat}</div>
        <div class="skills-grid">${rows}</div>
      </div>`;
  }

  html += `
    <div class="global-save-section" style="margin-top: 2rem; padding-top: 1.5rem; border-top: 1px solid var(--an-surface-deep); display: flex; justify-content: space-between; align-items: center;">
      <div id="save-status-msg" style="color: var(--an-muted-fg); font-style: italic; font-size: 0.9rem;">Skill profile saved</div>
      <button class="btn btn--primary" id="global-save-btn" onclick="saveAllSkills()" disabled>Save Skill Profile</button>
    </div>`;

  container.innerHTML = html;
}

function checkUnsavedChanges() {
  const selects = document.querySelectorAll('.level-select');
  let hasChanges = false;
  selects.forEach(sel => {
    if (sel.value !== sel.dataset.original) {
      hasChanges = true;
    }
  });

  const btn = document.getElementById('global-save-btn');
  const msg = document.getElementById('save-status-msg');
  if (btn && msg) {
    btn.disabled = !hasChanges;
    if (hasChanges) {
      msg.textContent = 'Unsaved changes';
      msg.style.color = 'var(--an-ember)';
    } else {
      msg.textContent = 'Skill profile saved';
      msg.style.color = 'var(--an-muted-fg)';
    }
  }
}

async function saveAllSkills() {
  const selects = document.querySelectorAll('.level-select');
  const updates = [];
  selects.forEach(sel => {
    if (sel.value !== sel.dataset.original) {
      updates.push({
        select: sel,
        skill_id: parseInt(sel.dataset.skillId, 10),
        current_level: parseInt(sel.value, 10)
      });
    }
  });

  if (updates.length === 0) return;

  const btn = document.getElementById('global-save-btn');
  const msg = document.getElementById('save-status-msg');
  btn.disabled = true;
  btn.textContent = 'Saving…';
  
  try {
    // The backend API expects one update at a time
    await Promise.all(updates.map(update => 
      fetch(`${API}/api/user/skills`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ skill_id: update.skill_id, current_level: update.current_level }),
      }).then(r => {
        if (!r.ok) throw new Error(`HTTP ${r.status}`);
        return r.json();
      })
    ));

    updates.forEach(update => {
      update.select.dataset.original = update.current_level;
    });

    btn.textContent = 'Save Skill Profile';
    checkUnsavedChanges();
    showToast('Skill profile updated successfully', 'success');
  } catch (err) {
    btn.textContent = 'Save Skill Profile';
    btn.disabled = false;
    showToast(`Save failed: ${err.message}`, 'error');
  }
}

window.saveAllSkills = saveAllSkills;
window.checkUnsavedChanges = checkUnsavedChanges;

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

  const rows = careers.map(career => {
    const isSelected = career.career_id === selectedId;
    const icon = CAREER_ICONS[career.career_name] || '💼';

    return `
      <div
        class="career-row ${isSelected ? 'career-row--selected' : ''}"
        id="career-card-${career.career_id}"
        onclick="selectCareer(${career.career_id}, '${career.career_name.replace(/'/g, "\\'")}')"
        role="button"
        tabindex="0"
        aria-pressed="${isSelected}"
      >
        <div class="career-row__info">
          <div class="career-row__icon">${icon}</div>
          <div class="career-row__name">${career.career_name}</div>
        </div>
        
        <div class="career-row__status">
          ${isSelected ? '<span class="badge badge--success">✓ Target</span>' : ''}
        </div>
        
        <div class="career-row__action">
          <button
            class="btn ${isSelected ? 'btn--selected' : 'btn--outline'}"
            onclick="event.stopPropagation(); selectAndNavigate(${career.career_id}, '${career.career_name.replace(/'/g, "\\'")}')"
          >
            ${isSelected ? 'Analyse Gap →' : 'Select'}
          </button>
        </div>
      </div>`;
  }).join('');

  container.innerHTML = `
    <div class="career-list" id="career-grid">${rows}</div>
    <p class="text-muted mt-6" style="font-size:0.85rem">
      Click a career row to set it as your target. Your skill gap analysis and roadmap will update automatically.
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
  
  initOnboarding();
  initHelp();
});

/* ============================================================
   Onboarding and Contextual Help
   ============================================================ */

const ONBOARDING_KEY = 'pathwise_onboarding_completed';

const ONBOARDING_STEPS = [
  {
    isWelcome: true,
    eyebrow: 'WELCOME TO PATHWISE',
    title: 'Find your next step.',
    content: `<p style="margin-top:0">PathWise helps you understand where you are now, where you want to go, and which skills to learn next.</p>
              <div class="welcome-path">
                <span class="step-num">01</span> &rarr; 
                <span class="step-num">02</span> &rarr; 
                <span class="step-num">03</span> &rarr; 
                <span class="step-num">04</span> &rarr; 
                <span class="step-num">05</span>
              </div>`
  },
  {
    title: 'My Skills',
    subtitle: 'Step 1 of 5',
    content: 'Tell PathWise where you are now. Rate your current skill proficiency from 1 (Beginner) to 5 (Expert).'
  },
  {
    title: 'Career Explorer',
    subtitle: 'Step 2 of 5',
    content: 'Choose where you want to go. Select a target career.'
  },
  {
    title: 'Skill Gap',
    subtitle: 'Step 3 of 5',
    content: 'See what separates your current profile from the target career. PathWise compares your current skills with the career requirements.'
  },
  {
    title: 'Recommendation',
    subtitle: 'Step 4 of 5',
    content: 'Find out what to learn next. The system uses your skill gap, priority score, and prerequisite logic to identify the next recommended skill.'
  },
  {
    title: 'Learning Roadmap',
    subtitle: 'Step 5 of 5',
    content: 'See the path forward. Your roadmap organizes skills in a prerequisite-safe order.'
  }
];

const HELP_CONTENT = {
  'index.html': {
    eyebrow: 'OVERVIEW',
    title: 'What is this page?',
    content: `<p style="margin-top:0">This page brings your career readiness into one view.</p>
              <div class="help-mini-guide">
                <div class="help-item">
                  <strong>CAREER FIT</strong>
                  <span>How closely your current profile matches the target career.</span>
                </div>
                <div class="help-item">
                  <strong>SKILL GAPS</strong>
                  <span>Where your current skill levels fall below requirements.</span>
                </div>
                <div class="help-item">
                  <strong>NEXT SKILL</strong>
                  <span>The skill PathWise currently prioritizes for you.</span>
                </div>
              </div>`
  },
  'skills.html': {
    eyebrow: 'YOUR STARTING POINT',
    title: 'What do I do here?',
    content: `<p style="margin-top:0">Rate your current skill levels. These values are used by PathWise to calculate your gaps and recommendations.</p>
              <div class="help-scale">
                <div class="help-scale-item"><strong>1</strong><span>Beginner</span></div>
                <div class="help-scale-item"><strong>2</strong><span>Basic</span></div>
                <div class="help-scale-item"><strong>3</strong><span>Intermediate</span></div>
                <div class="help-scale-item"><strong>4</strong><span>Advanced</span></div>
                <div class="help-scale-item"><strong>5</strong><span>Expert</span></div>
              </div>`
  },
  'careers.html': {
    eyebrow: 'YOUR DESTINATION',
    title: 'What do I do here?',
    content: `<p style="margin-top:0">Select the career you want to work toward.</p>
              <div class="help-flow">
                <div class="help-flow-box">CURRENT PROFILE</div>
                <div class="help-flow-arrow">&darr;</div>
                <div class="help-flow-box help-flow-box--target">TARGET CAREER</div>
              </div>`
  },
  'gap.html': {
    eyebrow: 'UNDERSTAND YOUR GAP',
    title: 'What does this mean?',
    content: `<p style="margin-top:0">PathWise compares your current skill levels with the requirements of your selected career.</p>
              <div class="help-mini-guide">
                <div class="help-item"><strong>CURRENT LEVEL</strong><span>Your present proficiency.</span></div>
                <div class="help-item"><strong>REQUIRED LEVEL</strong><span>The level expected for the target career.</span></div>
                <div class="help-item"><strong>GAP</strong><span>The difference between current and required level.</span></div>
                <div class="help-item"><strong>PRIORITY</strong><span>How strongly PathWise recommends developing the skill next.</span></div>
              </div>
              <div class="help-formula">
                <div class="formula-col">CURRENT<br><strong>3</strong></div>
                <div class="formula-col">REQUIRED<br><strong>5</strong></div>
                <div class="formula-col formula-col--accent">GAP<br><strong>2 LEVELS</strong></div>
              </div>
              <p class="help-note">Skills with larger gaps are not automatically recommended first; Priority Score and prerequisite logic are also considered.</p>`
  },
  'roadmap.html': {
    eyebrow: 'THE PATH FORWARD',
    title: 'What is this?',
    content: `<p style="margin-top:0">The roadmap organizes the skills you need to develop toward your selected career while respecting prerequisite relationships.</p>
              <div class="help-flow">
                <div class="help-flow-box">SKILL A</div>
                <div class="help-flow-arrow">&darr;</div>
                <div class="help-flow-box">SKILL B</div>
                <div class="help-flow-arrow">&darr;</div>
                <div class="help-flow-box help-flow-box--target">RECOMMENDED NEXT SKILL</div>
                <div class="help-flow-arrow">&darr;</div>
                <div class="help-flow-box help-flow-box--final">TARGET CAREER</div>
              </div>`
  }
};
HELP_CONTENT[''] = HELP_CONTENT['index.html'];

function getCurrentPageName() {
  const path = window.location.pathname;
  let page = path.split('/').pop();
  return page;
}

function initOnboarding() {
  // Only show on first visit (or when localStorage is cleared)
  if (localStorage.getItem(ONBOARDING_KEY)) return;

  const overlay = document.createElement('div');
  overlay.className = 'onboarding-overlay onboarding-overlay--anim';
  overlay.innerHTML = `
    <div class="onboarding-modal" role="dialog" aria-modal="true" aria-labelledby="ob-title">
      <div class="onboarding-modal__header">
        <span class="onboarding-modal__eyebrow" id="ob-eyebrow" style="display:none"></span>
        <h2 id="ob-title" class="onboarding-modal__title"></h2>
        <span class="onboarding-modal__subtitle" id="ob-subtitle"></span>
      </div>
      <div class="onboarding-modal__content" id="ob-content"></div>
      <div class="onboarding-modal__footer">
        <button class="btn btn--ghost" id="ob-skip-btn">Skip</button>
        <div style="flex:1"></div>
        <button class="btn btn--outline" id="ob-back-btn" style="display:none">Back</button>
        <button class="btn btn--primary" id="ob-next-btn">Next</button>
      </div>
    </div>
  `;
  document.body.appendChild(overlay);

  let currentStep = 0;
  const nextBtn = document.getElementById('ob-next-btn');

  function renderStep() {
    const step = ONBOARDING_STEPS[currentStep];
    
    if (step.isWelcome) {
      document.getElementById('ob-eyebrow').textContent = step.eyebrow;
      document.getElementById('ob-eyebrow').style.display = 'block';
      document.getElementById('ob-subtitle').style.display = 'none';
      document.querySelector('.onboarding-modal__header').classList.add('welcome-header');
    } else {
      document.getElementById('ob-eyebrow').style.display = 'none';
      document.getElementById('ob-subtitle').textContent = step.subtitle;
      document.getElementById('ob-subtitle').style.display = 'block';
      document.querySelector('.onboarding-modal__header').classList.remove('welcome-header');
    }

    document.getElementById('ob-title').textContent = step.title;
    document.getElementById('ob-content').innerHTML = step.content;

    document.getElementById('ob-back-btn').style.display = currentStep === 0 ? 'none' : 'block';
    
    if (currentStep === 0) {
      nextBtn.textContent = "Let's Begin →";
    } else if (currentStep === ONBOARDING_STEPS.length - 1) {
      nextBtn.textContent = 'Finish';
    } else {
      nextBtn.textContent = 'Next';
    }
    
    // Manage focus for accessibility
    nextBtn.focus();
  }

  function finish() {
    localStorage.setItem(ONBOARDING_KEY, 'true');
    overlay.classList.add('onboarding-overlay--closing');
    setTimeout(() => overlay.remove(), 250);
  }

  nextBtn.addEventListener('click', () => {
    if (currentStep < ONBOARDING_STEPS.length - 1) {
      currentStep++;
      renderStep();
    } else {
      finish();
    }
  });

  document.getElementById('ob-back-btn').addEventListener('click', () => {
    if (currentStep > 0) {
      currentStep--;
      renderStep();
    }
  });

  document.getElementById('ob-skip-btn').addEventListener('click', finish);

  renderStep();
}

function initHelp() {
  const page = getCurrentPageName();
  const helpData = HELP_CONTENT[page];
  if (!helpData) return;

  const header = document.querySelector('.page-header');
  if (!header) return;

  const helpBtn = document.createElement('button');
  helpBtn.className = 'help-btn';
  helpBtn.setAttribute('aria-label', 'Help');
  helpBtn.textContent = '?';
  helpBtn.onclick = () => {
    // If onboarding is open, ignore
    if (document.querySelector('.onboarding-overlay')) return;
    showHelpModal(helpData);
  };
  
  header.style.position = 'relative';
  header.style.paddingRight = '3rem';
  helpBtn.style.position = 'absolute';
  helpBtn.style.right = '0';
  helpBtn.style.top = '0';
  
  header.appendChild(helpBtn);
}

function showHelpModal(helpData) {
  const overlay = document.createElement('div');
  overlay.className = 'onboarding-overlay onboarding-overlay--anim';
  overlay.innerHTML = `
    <div class="onboarding-modal help-modal" role="dialog" aria-modal="true" aria-labelledby="help-title">
      <div class="help-modal__header">
        <span class="onboarding-modal__eyebrow">${helpData.eyebrow}</span>
      </div>
      <div class="onboarding-modal__header" style="border-bottom:none; margin-bottom: 0; padding-top: 0;">
        <h2 id="help-title" class="onboarding-modal__title">${helpData.title}</h2>
      </div>
      <div class="onboarding-modal__content" style="margin-bottom: 0; padding-top: 0.5rem;">${helpData.content}</div>
      <div class="onboarding-modal__footer" style="justify-content: space-between; border-top: none;">
        <span class="help-modal__hint">Press ESC to dismiss</span>
        <button class="btn btn--primary" id="help-close-btn">Close</button>
      </div>
    </div>
  `;
  document.body.appendChild(overlay);

  const closeBtn = document.getElementById('help-close-btn');
  const removeModal = () => {
    overlay.classList.add('onboarding-overlay--closing');
    setTimeout(() => overlay.remove(), 250);
  };
  
  closeBtn.addEventListener('click', removeModal);
  overlay.addEventListener('click', (e) => {
    if (e.target === overlay) removeModal();
  });
  
  closeBtn.focus();
  
  const handleEsc = (e) => {
    if (e.key === 'Escape') {
      removeModal();
      document.removeEventListener('keydown', handleEsc);
    }
  };
  document.addEventListener('keydown', handleEsc);
}
