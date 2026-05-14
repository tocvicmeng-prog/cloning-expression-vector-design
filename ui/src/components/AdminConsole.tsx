import { ClipboardList, SlidersHorizontal } from 'lucide-react';
import type { ReviewQueueItem } from '../types';

type AdminConsoleProps = {
  queue: ReviewQueueItem[];
  expertMode: boolean;
  onExpertModeChange: (enabled: boolean) => void;
  locale: string;
  onLocaleChange: (locale: string) => void;
};

export function AdminConsole({ queue, expertMode, onExpertModeChange, locale, onLocaleChange }: AdminConsoleProps) {
  return (
    <section className="panel admin-panel" aria-labelledby="admin-heading">
      <div className="panel-header compact">
        <div>
          <p className="eyebrow">Operations</p>
          <h2 id="admin-heading">Admin console</h2>
        </div>
        <ClipboardList size={22} />
      </div>

      <div className="console-controls">
        <label className="toggle-row">
          <input type="checkbox" checked={expertMode} onChange={(event) => onExpertModeChange(event.target.checked)} />
          <span>Expert mode</span>
        </label>
        <label className="select-row">
          <SlidersHorizontal size={16} />
          Locale
          <select value={locale} onChange={(event) => onLocaleChange(event.target.value)} aria-label="Locale">
            <option value="en-AU">en-AU</option>
            <option value="en-US">en-US</option>
            <option value="ja-JP">ja-JP</option>
          </select>
        </label>
      </div>

      <div className="queue-list" aria-label="Review queue">
        {queue.map((item) => (
          <article key={item.id} className="queue-row">
            <div>
              <h3>{item.designName}</h3>
              <p>{item.owner}</p>
            </div>
            <span className={`queue-status ${item.status.toLowerCase()}`}>{item.status}</span>
            <time>{item.submittedAt}</time>
          </article>
        ))}
      </div>
    </section>
  );
}
