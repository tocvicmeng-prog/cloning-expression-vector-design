import { CircleAlert, Clock3, Database, FileLock2, FlaskConical, LockKeyhole, ShieldCheck } from 'lucide-react';
import type { DesignSummary } from '../types';

type DesignSummaryBarProps = {
  summary: DesignSummary;
};

export function DesignSummaryBar({ summary }: DesignSummaryBarProps) {
  const metrics = [
    { label: 'Objective', value: summary.objective },
    { label: 'Host', value: summary.host },
    { label: 'Vector size', value: summary.vectorSize },
    { label: 'Locked modules', value: String(summary.lockedModules) }
  ];

  return (
    <section className="design-summary-band" aria-labelledby="design-summary-heading">
      <div className="design-summary-title">
        <FlaskConical size={24} />
        <div>
          <p className="eyebrow">Current design</p>
          <h2 id="design-summary-heading">{summary.designId}</h2>
          <span>
            {summary.owner} · {summary.version}
          </span>
        </div>
      </div>

      <dl className="summary-metrics">
        {metrics.map((metric) => (
          <div key={metric.label}>
            <dt>{metric.label}</dt>
            <dd>{metric.value}</dd>
          </div>
        ))}
      </dl>

      <div className="summary-state" aria-label="Design readiness">
        <span className="summary-chip warning">
          <CircleAlert size={15} />
          {summary.exportReadiness}
        </span>
        <span className="summary-chip">
          <ShieldCheck size={15} />
          {summary.reviewState}
        </span>
        <span className="summary-chip">
          <LockKeyhole size={15} />
          Review gated
        </span>
        <span className="summary-chip muted">
          <Clock3 size={15} />
          {summary.lastSaved}
        </span>
        <span className="summary-chip muted">
          <Database size={15} />
          Traceable draft
        </span>
        <span className="summary-chip muted">
          <FileLock2 size={15} />
          Audit ready
        </span>
      </div>
    </section>
  );
}
