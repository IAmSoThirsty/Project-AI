/* ── Storm Desk — Settings Panel ─────────────────────────────────── */

import type { UserSettings } from '../types';
import { getAllChannels } from '../channels';

type SettingsCallback = (updated: UserSettings) => void;

export function renderSettingsPanel(
  container: HTMLElement,
  settings: UserSettings,
  onSave: SettingsCallback,
): void {
  const channels = getAllChannels();

  const channelOptions = channels
    .map(
      (c) =>
        `<option value="${escapeAttr(c.name)}" ${c.name === settings.pinnedChannel ? 'selected' : ''}>${escapeAttr(c.name)} [${c.health}]</option>`,
    )
    .join('');

  container.innerHTML = `
    <div class="settings-card">
      <h2 class="settings-title">Settings</h2>
      <form id="settings-form" class="settings-form">
        <fieldset>
          <legend>Display</legend>
          <label>
            Pinned channel
            <select name="pinnedChannel">${channelOptions}</select>
          </label>
          <label>
            Rotation interval (seconds)
            <input type="number" name="rotationIntervalMs" min="5" max="300"
              value="${settings.rotationIntervalMs / 1000}" step="1" />
          </label>
          <label>
            Max micro viewers
            <input type="number" name="maxMicroViewers" min="1" max="12"
              value="${settings.maxMicroViewers}" />
          </label>
          <label class="settings-check">
            <input type="checkbox" name="muteMicroFeeds" ${settings.muteMicroFeeds ? 'checked' : ''} />
            Mute micro feeds
          </label>
          <label>
            Theme
            <select name="theme">
              <option value="dark" ${settings.theme === 'dark' ? 'selected' : ''}>Dark</option>
              <option value="light" ${settings.theme === 'light' ? 'selected' : ''}>Light</option>
            </select>
          </label>
        </fieldset>

        <fieldset>
          <legend>Escalation</legend>
          <label class="settings-check">
            <input type="checkbox" name="autoEscalate" ${settings.autoEscalate ? 'checked' : ''} />
            Auto-escalate on major events
          </label>
          <label>
            Minimum score for escalation
            <input type="number" name="minScoreForEscalation" min="0" max="100"
              value="${settings.minScoreForEscalation}" />
          </label>
          <label>
            Minimum independent sources
            <input type="number" name="minSourcesForEscalation" min="1" max="10"
              value="${settings.minSourcesForEscalation}" />
          </label>
          <label class="settings-check">
            <input type="checkbox" name="requireWireForEscalation"
              ${settings.requireWireForEscalation ? 'checked' : ''} />
            Require wire service confirmation
          </label>
        </fieldset>

        <fieldset>
          <legend>Notifications</legend>
          <label class="settings-check">
            <input type="checkbox" name="notificationsEnabled"
              ${settings.notificationsEnabled ? 'checked' : ''} />
            Enable desktop notifications
          </label>
        </fieldset>

        <div class="settings-actions">
          <button type="submit" class="storm-btn storm-btn-primary">Save</button>
          <button type="button" class="storm-btn" id="settings-cancel">Cancel</button>
        </div>
      </form>
    </div>
  `;

  const form = container.querySelector('#settings-form') as HTMLFormElement;
  const cancelBtn = container.querySelector('#settings-cancel') as HTMLButtonElement;

  form.addEventListener('submit', (e) => {
    e.preventDefault();
    const fd = new FormData(form);

    const updated: UserSettings = {
      pinnedChannel: fd.get('pinnedChannel') as string,
      rotationIntervalMs: Number(fd.get('rotationIntervalMs')) * 1000,
      maxMicroViewers: Number(fd.get('maxMicroViewers')),
      muteMicroFeeds: fd.has('muteMicroFeeds'),
      theme: fd.get('theme') as 'dark' | 'light',
      autoEscalate: fd.has('autoEscalate'),
      minScoreForEscalation: Number(fd.get('minScoreForEscalation')),
      minSourcesForEscalation: Number(fd.get('minSourcesForEscalation')),
      requireWireForEscalation: fd.has('requireWireForEscalation'),
      notificationsEnabled: fd.has('notificationsEnabled'),
    };

    persistSettings(updated);
    onSave(updated);
    container.classList.add('hidden');
  });

  cancelBtn.addEventListener('click', () => {
    container.classList.add('hidden');
  });
}

function persistSettings(settings: UserSettings): void {
  try {
    localStorage.setItem('storm-desk-settings', JSON.stringify(settings));
  } catch {
    /* storage unavailable in some contexts */
  }
}

export function loadPersistedSettings(): UserSettings | null {
  try {
    const raw = localStorage.getItem('storm-desk-settings');
    if (!raw) return null;
    return JSON.parse(raw) as UserSettings;
  } catch {
    return null;
  }
}

function escapeAttr(str: string): string {
  return str
    .replace(/&/g, '&amp;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;');
}
