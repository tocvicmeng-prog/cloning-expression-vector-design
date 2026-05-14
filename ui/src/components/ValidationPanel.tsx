import { AlertTriangle, CheckCircle2, CircleX } from 'lucide-react';
import type { ValidationFinding, ValidationSeverity } from '../types';

const severityIcon = {
  pass: CheckCircle2,
  warn: AlertTriangle,
  error: CircleX
} satisfies Record<ValidationSeverity, typeof CheckCircle2>;

type ValidationPanelProps = {
  findings: ValidationFinding[];
  onModuleSelect: (moduleId: string) => void;
};

export function ValidationPanel({ findings, onModuleSelect }: ValidationPanelProps) {
  const warningCount = findings.filter((finding) => finding.severity === 'warn').length;

  return (
    <section className="panel validation-panel" aria-labelledby="validation-heading">
      <div className="panel-header compact">
        <div>
          <p className="eyebrow">Live checks</p>
          <h2 id="validation-heading">Validation report</h2>
        </div>
        <span className="status-chip">{warningCount} warnings</span>
      </div>

      <div className="finding-list">
        {findings.map((finding) => {
          const Icon = severityIcon[finding.severity];

          return (
            <button
              key={finding.id}
              type="button"
              className={`finding-row ${finding.severity}`}
              onClick={() => onModuleSelect(finding.moduleId)}
            >
              <Icon size={18} />
              <span>
                <strong>{finding.moduleLabel}</strong>
                {finding.message}
              </span>
            </button>
          );
        })}
      </div>
    </section>
  );
}
