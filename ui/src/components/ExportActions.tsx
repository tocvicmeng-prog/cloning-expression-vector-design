import { CheckCircle2, FileArchive, Send, ShieldAlert } from 'lucide-react';
import type { ExportAction } from '../types';

const actionIcon = {
  'validate-design': CheckCircle2,
  'draft-bundle': FileArchive,
  'submit-review': Send,
  'final-export': ShieldAlert
};

type ExportActionsProps = {
  actions: ExportAction[];
};

export function ExportActions({ actions }: ExportActionsProps) {
  return (
    <section className="panel export-panel" aria-labelledby="export-heading">
      <div className="panel-header compact">
        <div>
          <p className="eyebrow">Output</p>
          <h2 id="export-heading">Action and export</h2>
        </div>
      </div>

      <div className="export-action-list">
        {actions.map((action) => {
          const Icon = actionIcon[action.id as keyof typeof actionIcon] ?? FileArchive;

          return (
            <button
              key={action.id}
              type="button"
              className={`export-action ${action.state}`}
              disabled={action.state === 'blocked'}
            >
              <Icon size={18} />
              <span>
                <strong>{action.label}</strong>
                {action.description}
              </span>
              <em>{action.state}</em>
            </button>
          );
        })}
      </div>
    </section>
  );
}
