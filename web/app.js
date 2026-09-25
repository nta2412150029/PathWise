/**
 * app.js — PathWise frontend skeleton
 * Full page logic will be implemented in the UI phase.
 * This file currently only runs an API health check on the Dashboard.
 */

const API = '';   // Same origin — Flask serves both API and static files

/**
 * Fetch wrapper: returns parsed JSON or throws with the error message.
 */
async function apiFetch(path) {
  const res = await fetch(API + path);
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`HTTP ${res.status}: ${text}`);
  }
  return res.json();
}

/**
 * Dashboard health check — confirms the API is reachable.
 * Runs only when the #api-status element is present (index.html).
 */
async function runDashboardHealthCheck() {
  const el = document.getElementById('api-status');
  if (!el) return;

  try {
    const [careers, skills] = await Promise.all([
      apiFetch('/api/careers'),
      apiFetch('/api/skills'),
    ]);
    el.style.color = 'var(--color-success)';
    el.textContent =
      `✓ API connected — ${careers.length} careers, ${skills.length} skills loaded.`;
  } catch (err) {
    el.style.color = 'var(--color-danger)';
    el.textContent = `✗ API error: ${err.message}`;
  }
}

// Entry point
document.addEventListener('DOMContentLoaded', () => {
  runDashboardHealthCheck();
});
