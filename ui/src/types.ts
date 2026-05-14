export type Citation = {
  id: string;
  title: string;
  source: string;
};

export type WizardStep = {
  id: string;
  label: string;
  value: string;
  defaultValue: string;
  options: string[];
  tooltip: string;
  citation: Citation;
};

export type VectorFeature = {
  id: string;
  label: string;
  kind: 'promoter' | 'orf' | 'tag' | 'terminator' | 'resistance' | 'origin';
  start: number;
  end: number;
  strand: '+' | '-';
  source: string;
  locked: boolean;
  validation: ValidationSeverity;
};

export type ValidationSeverity = 'pass' | 'warn' | 'error';

export type DesignSummary = {
  designId: string;
  owner: string;
  version: string;
  vectorSize: string;
  objective: string;
  host: string;
  reviewState: string;
  exportReadiness: string;
  lockedModules: number;
  lastSaved: string;
};

export type WorkflowStageStatus = 'complete' | 'active' | 'warning' | 'blocked' | 'pending';

export type WorkflowStage = {
  id: string;
  label: string;
  summary: string;
  status: WorkflowStageStatus;
  moduleId?: string;
};

export type CompatibilityCheck = {
  id: string;
  axis: string;
  selection: string;
  status: ValidationSeverity;
  evidence: string;
  moduleId: string;
};

export type ImportChannel = {
  id: string;
  label: string;
  value: string;
  status: 'ready' | 'needed' | 'locked';
};

export type ExportAction = {
  id: string;
  label: string;
  description: string;
  state: 'ready' | 'blocked' | 'queued';
};

export type ValidationFinding = {
  id: string;
  moduleId: string;
  moduleLabel: string;
  severity: ValidationSeverity;
  message: string;
};

export type Advisory = {
  id: string;
  title: string;
  severity: 'controlled' | 'institutional' | 'documentation';
  moduleLabel: string;
  summary: string;
};

export type AuditRecord = {
  id: string;
  actor: string;
  action: string;
  target: string;
  timestamp: string;
};

export type ReviewQueueItem = {
  id: string;
  designName: string;
  owner: string;
  status: 'Pending' | 'Escalated' | 'Declined';
  submittedAt: string;
};
