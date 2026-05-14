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
  locked: boolean;
};

export type ValidationSeverity = 'pass' | 'warn' | 'error';

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
