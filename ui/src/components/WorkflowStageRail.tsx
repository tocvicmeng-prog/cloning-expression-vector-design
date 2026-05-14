import { AlertTriangle, CheckCircle2, Circle, CircleDot, CircleSlash2 } from 'lucide-react';
import type { WorkflowStage, WorkflowStageStatus } from '../types';

const statusIcon = {
  complete: CheckCircle2,
  active: CircleDot,
  warning: AlertTriangle,
  blocked: CircleSlash2,
  pending: Circle
} satisfies Record<WorkflowStageStatus, typeof CheckCircle2>;

type WorkflowStageRailProps = {
  stages: WorkflowStage[];
  activeStepId: string;
  onStageSelect: (stepId: string) => void;
};

export function WorkflowStageRail({ stages, activeStepId, onStageSelect }: WorkflowStageRailProps) {
  return (
    <section className="panel workflow-panel" aria-labelledby="workflow-heading">
      <div className="panel-header compact">
        <div>
          <p className="eyebrow">Wet-lab logic</p>
          <h2 id="workflow-heading">Workflow stages</h2>
        </div>
      </div>

      <div className="workflow-stage-list">
        {stages.map((stage, index) => {
          const status = stage.moduleId === activeStepId ? 'active' : stage.status;
          const Icon = statusIcon[status];

          return (
            <button
              key={stage.id}
              type="button"
              className={`workflow-stage ${status}`}
              onClick={() => stage.moduleId && onStageSelect(stage.moduleId)}
            >
              <span className="workflow-index">{String(index + 1).padStart(2, '0')}</span>
              <Icon size={17} />
              <span>
                <strong>{stage.label}</strong>
                {stage.summary}
              </span>
            </button>
          );
        })}
      </div>
    </section>
  );
}
