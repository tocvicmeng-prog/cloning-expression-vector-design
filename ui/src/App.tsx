import { useMemo, useState } from 'react';
import { Activity, FlaskConical, LayoutDashboard, ShieldCheck } from 'lucide-react';
import { AdvisoryActions } from './components/AdvisoryActions';
import { AdminConsole } from './components/AdminConsole';
import { AuditTrail } from './components/AuditTrail';
import { CompatibilityMatrix } from './components/CompatibilityMatrix';
import { DecisionWizard } from './components/DecisionWizard';
import { DesignSummaryBar } from './components/DesignSummaryBar';
import { DesignDiff } from './components/DesignDiff';
import { ExportActions } from './components/ExportActions';
import { InputImportPanel } from './components/InputImportPanel';
import { ValidationPanel } from './components/ValidationPanel';
import { VectorWorkspace } from './components/VectorWorkspace';
import { WorkflowStageRail } from './components/WorkflowStageRail';
import {
  advisories,
  auditRecords,
  compatibilityChecks,
  designSummary,
  exportActions,
  importChannels,
  reviewQueue,
  validationFindings,
  vectorFeatures,
  workflowStages,
  wizardSteps
} from './data';

type AdvisoryAction = 'acknowledge' | 'decline' | 'escalate';

const GMEXPRESSION_LOGO_URL = 'https://shop.gmexpression.com/image/catalog/logo/GMExpression_logo.png?v=1.3';

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
          <span>Cloning &amp; Expression Vector Design Toolkit</span>
        </div>
        <div className="nav-actions">
          <a className="nav-icon-link" href="#decision-heading" aria-label="Decision tree">
            <LayoutDashboard size={19} />
          </a>
          <a className="nav-icon-link" href="#vector-heading" aria-label="Vector map">
            <Activity size={19} />
          </a>
          <a className="nav-icon-link" href="#advisory-heading" aria-label="Advisory review">
            <ShieldCheck size={19} />
          </a>
          <a
            className="gmexpression-link"
            href="https://shop.gmexpression.com/"
            target="_blank"
            rel="noreferrer"
            aria-label="GMExpression shop"
          >
            <img src={GMEXPRESSION_LOGO_URL} alt="GMExpression" />
            <span>GMExpression</span>
          </a>
        </div>
      </nav>

      <div className="workspace">
        <DesignSummaryBar
          summary={{
            ...designSummary,
            objective: steps.find((step) => step.id === 'objective')?.value ?? designSummary.objective,
            host: steps.find((step) => step.id === 'host')?.value ?? designSummary.host,
            lockedModules: lockedStepIds.size
          }}
        />

        <aside className="workflow-column" aria-label="Design workflow">
          <WorkflowStageRail stages={workflowStages} activeStepId={activeStepId} onStageSelect={setActiveStepId} />
          <InputImportPanel channels={importChannels} />
        </aside>

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
          <CompatibilityMatrix checks={compatibilityChecks} onModuleSelect={setActiveStepId} />
          <DesignDiff />
        </div>

        <aside className="secondary-column" aria-label="Review and operations">
          <ValidationPanel findings={validationFindings} onModuleSelect={setActiveStepId} />
          <ExportActions actions={exportActions} />
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

      <footer className="gmexpression-footer" aria-label="GMExpression information">
        <div className="gmexpression-footer-inner">
          <div className="gmexpression-footer-title">
            GMExpression &middot; Cloning &amp; Expression Vector Design Toolkit
          </div>
          <div className="gmexpression-footer-copy">
            Created by GMExpression &middot; Data from authorised research publications &amp; databases (NCBI/NIH,
            DSMZ, IJSEM, CLSI, ISO, WHO).
          </div>
          <div className="gmexpression-footer-copy">&copy; 2026 GMExpression &middot; All rights reserved.</div>
          <div className="gmexpression-footer-links" aria-label="GMExpression links">
            <a href="https://www.gmexpression.com/" target="_blank" rel="noreferrer">
              GMExpression.com
            </a>
            <a href="https://shop.gmexpression.com/" target="_blank" rel="noreferrer">
              shop.gmexpression.com
            </a>
          </div>
          <div className="gmexpression-footer-disclaimer">
            For Research Use Only. Not intended for clinical, diagnostic, or therapeutic purposes. Always comply with
            institutional biosafety and regulatory requirements.
          </div>
        </div>
      </footer>
    </main>
  );
}

export default App;
