/* ── Storm Desk — Entry Point ────────────────────────────────────── */

import { boot } from './app';

document.addEventListener('DOMContentLoaded', () => {
  boot().catch((err) => {
    console.error('[storm-desk] Fatal boot error:', err);
    const root = document.getElementById('app');
    if (root) {
      root.innerHTML = `
        <div style="color:#ff4444;padding:2rem;font-family:monospace;">
          <h1>Storm Desk failed to initialize</h1>
          <pre>${String(err)}</pre>
        </div>`;
    }
  });
});
