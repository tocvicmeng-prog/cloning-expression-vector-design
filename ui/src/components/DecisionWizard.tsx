import { BookOpen, Check, HelpCircle, Lock, RefreshCw } from 'lucide-react';
import type { WizardStep } from '../types';

type DecisionWizardProps = {
  steps: WizardStep[];
  activeStepId: string;
  lockedStepIds: Set<string>;
  specialisedNotes: string;
  onActiveStepChange: (stepId: string) => void;
  onStepValueChange: (stepId: string, value: string) => void;
  onToggleLock: (stepId: string) => void;
  onNotesChange: (notes: string) => void;
};

export function DecisionWizard({
  steps,
  activeStepId,
  lockedStepIds,
  specialisedNotes,
  onActiveStepChange,
  onStepValueChange,
  onToggleLock,
  onNotesChange
}: DecisionWizardProps) {
  const activeStep = steps.find((step) => step.id === activeStepId) ?? steps[0];

  return (
    <section className="panel decision-panel" aria-labelledby="decision-heading">
      <div className="panel-header">
        <div>
          <p className="eyebrow">Decision tree</p>
          <h1 id="decision-heading">Vector Design Workspace</h1>
        </div>
        <div className="header-actions" aria-label="Decision tree tools">
          <button type="button" className="icon-button" title="Rerun from active step" aria-label="Rerun from active step">
            <RefreshCw size={18} />
          </button>
          <button type="button" className="icon-button" title="Accepted steps" aria-label="Accepted steps">
            <Check size={18} />
          </button>
        </div>
      </div>

      <div className="stepper" aria-label="Decision steps">
        {steps.map((step, index) => {
          const isActive = step.id === activeStep.id;
          const isLocked = lockedStepIds.has(step.id);

          return (
            <button
              key={step.id}
              type="button"
              className={`step-pill${isActive ? ' active' : ''}${isLocked ? ' locked' : ''}`}
              onClick={() => onActiveStepChange(step.id)}
            >
              <span>{String(index + 1).padStart(2, '0')}</span>
              {step.label}
            </button>
          );
        })}
      </div>

      <div className="wizard-grid">
        <div className="field-stack">
          <label htmlFor={`${activeStep.id}-select`}>
            {activeStep.label}
            <span className="tooltip-anchor" title={activeStep.tooltip} aria-label={`${activeStep.label} guidance`}>
              <HelpCircle size={16} />
            </span>
          </label>
          <select
            id={`${activeStep.id}-select`}
            value={activeStep.value}
            onChange={(event) => onStepValueChange(activeStep.id, event.target.value)}
          >
            {activeStep.options.map((option) => (
              <option key={option} value={option}>
                {option} [{activeStep.citation.id}]
              </option>
            ))}
          </select>

          <label htmlFor="specialised-requirement">Other / specialised - describe your requirement</label>
          <textarea
            id="specialised-requirement"
            maxLength={2000}
            value={specialisedNotes}
            onChange={(event) => onNotesChange(event.target.value)}
          />
          <div className="character-count">{specialisedNotes.length}/2000</div>
        </div>

        <aside className="why-panel" aria-labelledby="why-default-heading">
          <div className="why-panel-heading">
            <BookOpen size={18} />
            <h2 id="why-default-heading">Why this default?</h2>
          </div>
          <p>{activeStep.defaultValue}</p>
          <dl>
            <div>
              <dt>Citation</dt>
              <dd>
                {activeStep.citation.id}: {activeStep.citation.title}
              </dd>
            </div>
            <div>
              <dt>Source</dt>
              <dd>{activeStep.citation.source}</dd>
            </div>
          </dl>
          <button
            type="button"
            className={`lock-button${lockedStepIds.has(activeStep.id) ? ' locked' : ''}`}
            onClick={() => onToggleLock(activeStep.id)}
            aria-pressed={lockedStepIds.has(activeStep.id)}
          >
            <Lock size={17} />
            {lockedStepIds.has(activeStep.id) ? 'Locked' : 'Lock module'}
          </button>
        </aside>
      </div>
    </section>
  );
}
