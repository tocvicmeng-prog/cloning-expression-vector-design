import { GitCompareArrows } from 'lucide-react';

export function DesignDiff() {
  return (
    <section className="panel diff-panel" aria-labelledby="diff-heading">
      <div className="panel-header compact">
        <div>
          <p className="eyebrow">Revision</p>
          <h2 id="diff-heading">Design diff</h2>
        </div>
        <GitCompareArrows size={22} />
      </div>

      <div className="diff-grid">
        <div>
          <h3>Current</h3>
          <p>Inducible promoter retained with C-terminal fusion tag.</p>
        </div>
        <div>
          <h3>Proposed</h3>
          <p>Specialised objective notes route the design through review before export.</p>
        </div>
      </div>
    </section>
  );
}
