import { AlertTriangle, CheckCircle2, CircleX } from 'lucide-react';
import type { CompatibilityCheck, ValidationSeverity } from '../types';

const severityIcon = {
  pass: CheckCircle2,
  warn: AlertTriangle,
  error: CircleX
} satisfies Record<ValidationSeverity, typeof CheckCircle2>;

type CompatibilityMatrixProps = {
  checks: CompatibilityCheck[];
  onModuleSelect: (moduleId: string) => void;
};

export function CompatibilityMatrix({ checks, onModuleSelect }: CompatibilityMatrixProps) {
  return (
    <section className="panel compatibility-panel" aria-labelledby="compatibility-heading">
      <div className="panel-header compact">
        <div>
          <p className="eyebrow">Feasibility</p>
          <h2 id="compatibility-heading">Compatibility matrix</h2>
        </div>
        <span className="status-chip">{checks.filter((check) => check.status === 'warn').length} warnings</span>
      </div>

      <div className="compatibility-grid">
        {checks.map((check) => {
          const Icon = severityIcon[check.status];

          return (
            <button
              key={check.id}
              type="button"
              className={`compatibility-row ${check.status}`}
              onClick={() => onModuleSelect(check.moduleId)}
            >
              <Icon size={18} />
              <span>
                <strong>{check.axis}</strong>
                <em>{check.selection}</em>
                {check.evidence}
              </span>
            </button>
          );
        })}
      </div>
    </section>
  );
}
