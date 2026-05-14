import { CheckCircle2, CornerUpRight, ShieldAlert, XCircle } from 'lucide-react';
import type { Advisory } from '../types';

type AdvisoryAction = 'acknowledge' | 'decline' | 'escalate';

type AdvisoryActionsProps = {
  advisories: Advisory[];
  action: AdvisoryAction | null;
  justification: string;
  approvalId: string;
  onActionChange: (action: AdvisoryAction) => void;
  onJustificationChange: (value: string) => void;
  onApprovalIdChange: (value: string) => void;
};

export function AdvisoryActions({
  advisories,
  action,
  justification,
  approvalId,
  onActionChange,
  onJustificationChange,
  onApprovalIdChange
}: AdvisoryActionsProps) {
  const canCommit =
    action === 'decline' ||
    (action === 'acknowledge' && justification.trim().length >= 20) ||
    (action === 'escalate' && approvalId.trim().length >= 6 && justification.trim().length >= 20);

  return (
    <section
      className="panel advisory-panel"
      role="dialog"
      aria-modal="false"
      aria-labelledby="advisory-heading"
      data-testid="advisory-actions"
    >
      <div className="panel-header compact">
        <div>
          <p className="eyebrow">Advisory gate</p>
          <h2 id="advisory-heading">Review decision</h2>
        </div>
        <ShieldAlert size={22} aria-hidden="true" />
      </div>

      <div className="advisory-list">
        {advisories.map((advisory) => (
          <article key={advisory.id} className={`advisory-item ${advisory.severity}`}>
            <h3>{advisory.title}</h3>
            <p>{advisory.summary}</p>
            <span>{advisory.moduleLabel}</span>
          </article>
        ))}
      </div>

      <div className="action-strip" role="group" aria-label="Advisory decision actions">
        <button
          type="button"
          className={action === 'acknowledge' ? 'selected' : ''}
          onClick={() => onActionChange('acknowledge')}
        >
          <CheckCircle2 size={17} />
          Acknowledge
        </button>
        <button type="button" className={action === 'decline' ? 'selected' : ''} onClick={() => onActionChange('decline')}>
          <XCircle size={17} />
          Decline
        </button>
        <button
          type="button"
          className={action === 'escalate' ? 'selected' : ''}
          onClick={() => onActionChange('escalate')}
        >
          <CornerUpRight size={17} />
          Escalate
        </button>
      </div>

      <label htmlFor="advisory-justification">Justification record</label>
      <textarea
        id="advisory-justification"
        value={justification}
        onChange={(event) => onJustificationChange(event.target.value)}
      />

      {action === 'escalate' ? (
        <div className="field-stack tight">
          <label htmlFor="approval-id">Institutional approval ID</label>
          <input id="approval-id" value={approvalId} onChange={(event) => onApprovalIdChange(event.target.value)} />
        </div>
      ) : null}

      <button type="button" className="commit-button" disabled={!canCommit}>
        Record decision
      </button>
    </section>
  );
}
