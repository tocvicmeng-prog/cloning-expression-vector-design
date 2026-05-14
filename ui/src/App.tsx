import { useMemo, useState } from 'react';
import { Activity, FlaskConical, LayoutDashboard, ShieldCheck } from 'lucide-react';
import { AdvisoryActions } from './components/AdvisoryActions';
import { AdminConsole } from './components/AdminConsole';
import { AuditTrail } from './components/AuditTrail';
import { DecisionWizard } from './components/DecisionWizard';
import { DesignDiff } from './components/DesignDiff';
import { ValidationPanel } from './components/ValidationPanel';
import { VectorWorkspace } from './components/VectorWorkspace';
import { advisories, auditRecords, reviewQueue, validationFindings, vectorFeatures, wizardSteps } from './data';

type AdvisoryAction = 'acknowledge' | 'decline' | 'escalate';

function App() {
  const [steps, setSteps] = useState(wizardSteps);
  const [activeStepId, setActiveStepId] = useState(wizardSteps[0].id);
  const [lockedStepIds, setLockedStepIds] = useState<Set<string>>(() => new Set(['objective']));
  const [specialisedNotes, setSpecialisedNotes] = useState('');
  const [zoom, setZoom] = useState(4200);
  const [advisoryAction, setAdvisoryAction] = useState<AdvisoryAction | null>(null);
  const [justification, setJustification] = useState('');
  const [approvalId, setApprovalId] = useState('');
  const [expertMode, setExpertMode] = useState(false);
  const [locale, setLocale] = useState('en-AU');

  const selectedStep = useMemo(() => steps.find((step) => step.id === activeStepId) ?? steps[0], [activeStepId, steps]);

  function handleStepValueChange(stepId: string, value: string) {
    setSteps((current) => current.map((step) => (step.id === stepId ? { ...step, value } : step)));
  }

  function handleToggleLock(stepId: string) {
    setLockedStepIds((current) => {
      const next = new Set(current);
      if (next.has(stepId)) {
        next.delete(stepId);
      } else {
        next.add(stepId);
      }
      return next;
    });
  }

  return (
    <main className="app-shell">
      <nav className="workspace-nav" aria-label="Workspace sections">
        <div className="brand-mark">
          <FlaskConical size={23} />
          <span>Vector Design</span>
        </div>
        <a href="#decision-heading" aria-label="Decision tree">
          <LayoutDashboard size={19} />
        </a>
        <a href="#vector-heading" aria-label="Vector map">
          <Activity size={19} />
        </a>
        <a href="#advisory-heading" aria-label="Advisory review">
          <ShieldCheck size={19} />
        </a>
      </nav>

      <div className="workspace">
        <div className="primary-column">
          <DecisionWizard
            steps={steps}
            activeStepId={selectedStep.id}
            lockedStepIds={lockedStepIds}
            specialisedNotes={specialisedNotes}
            onActiveStepChange={setActiveStepId}
            onStepValueChange={handleStepValueChange}
            onToggleLock={handleToggleLock}
            onNotesChange={setSpecialisedNotes}
          />
          <VectorWorkspace features={vectorFeatures} zoom={zoom} onZoomChange={setZoom} />
          <DesignDiff />
        </div>

        <aside className="secondary-column" aria-label="Review and operations">
          <ValidationPanel findings={validationFindings} onModuleSelect={setActiveStepId} />
          <AdvisoryActions
            advisories={advisories}
            action={advisoryAction}
            justification={justification}
            approvalId={approvalId}
            onActionChange={setAdvisoryAction}
            onJustificationChange={setJustification}
            onApprovalIdChange={setApprovalId}
          />
          <AdminConsole
            queue={reviewQueue}
            expertMode={expertMode}
            onExpertModeChange={setExpertMode}
            locale={locale}
            onLocaleChange={setLocale}
          />
          <AuditTrail records={auditRecords} />
        </aside>
      </div>
    </main>
  );
}

export default App;
