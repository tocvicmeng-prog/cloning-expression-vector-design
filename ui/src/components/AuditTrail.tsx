import { History } from 'lucide-react';
import type { AuditRecord } from '../types';

type AuditTrailProps = {
  records: AuditRecord[];
};

export function AuditTrail({ records }: AuditTrailProps) {
  return (
    <section className="panel audit-panel" aria-labelledby="audit-heading">
      <div className="panel-header compact">
        <div>
          <p className="eyebrow">Evidence</p>
          <h2 id="audit-heading">Audit log</h2>
        </div>
        <History size={22} />
      </div>
      <table>
        <thead>
          <tr>
            <th>Time</th>
            <th>Actor</th>
            <th>Action</th>
            <th>Target</th>
          </tr>
        </thead>
        <tbody>
          {records.map((record) => (
            <tr key={record.id}>
              <td>{record.timestamp}</td>
              <td>{record.actor}</td>
              <td>{record.action}</td>
              <td>{record.target}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </section>
  );
}
