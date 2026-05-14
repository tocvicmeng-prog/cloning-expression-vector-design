import type {
  Advisory,
  AuditRecord,
  CompatibilityCheck,
  DesignSummary,
  ExportAction,
  ImportChannel,
  ReviewQueueItem,
  ValidationFinding,
  VectorFeature,
  WorkflowStage,
  WizardStep
} from './types';

export const wizardSteps: WizardStep[] = [
  {
    id: 'objective',
    label: 'Objective',
    value: 'Screen expression panel',
    defaultValue: 'Screen expression panel',
    options: ['Screen expression panel', 'Purify soluble protein', 'Reporter assay', 'Other / specialised'],
    tooltip: 'Defines the decision-tree branch and downstream validation policy.',
    citation: {
      id: 'WP-01',
      title: 'Design objectives matrix',
      source: 'Internal white paper, section 2.1'
    }
  },
  {
    id: 'host',
    label: 'Target host',
    value: 'E. coli K-12 derivative',
    defaultValue: 'E. coli K-12 derivative',
    options: ['E. coli K-12 derivative', 'B. subtilis', 'S. cerevisiae', 'Mammalian transient', 'Other / specialised'],
    tooltip: 'Host selection controls promoter, origin, resistance, and biosafety checks.',
    citation: {
      id: 'WP-04',
      title: 'Host compatibility catalogue',
      source: 'Internal white paper, section 3.4'
    }
  },
  {
    id: 'cargo',
    label: 'Cargo type',
    value: 'Open reading frame',
    defaultValue: 'Open reading frame',
    options: ['Open reading frame', 'Signal peptide fusion', 'Reporter cassette', 'Guide scaffold', 'Other / specialised'],
    tooltip: 'Cargo type drives ORF frame, fusion, and annotation requirements.',
    citation: {
      id: 'WP-06',
      title: 'Cargo annotation defaults',
      source: 'Internal white paper, section 4.2'
    }
  },
  {
    id: 'expression',
    label: 'Expression / induction',
    value: 'Tunable inducible',
    defaultValue: 'Tunable inducible',
    options: ['Constitutive low', 'Tunable inducible', 'Tight repression', 'No expression cassette', 'Other / specialised'],
    tooltip: 'Expression mode determines promoter defaults and warning thresholds.',
    citation: {
      id: 'WP-09',
      title: 'Expression-control defaults',
      source: 'Internal white paper, section 5.1'
    }
  },
  {
    id: 'tagging',
    label: 'Tagging',
    value: 'C-terminal 6xHis',
    defaultValue: 'C-terminal 6xHis',
    options: ['None', 'N-terminal 6xHis', 'C-terminal 6xHis', 'Dual tag', 'Other / specialised'],
    tooltip: 'Tag placement is checked against translation frame and stop codon placement.',
    citation: {
      id: 'WP-12',
      title: 'Fusion tag policy',
      source: 'Internal white paper, section 6.3'
    }
  },
  {
    id: 'chemistry',
    label: 'Cloning chemistry',
    value: 'Golden Gate assembly',
    defaultValue: 'Golden Gate assembly',
    options: ['Golden Gate assembly', 'Gibson assembly', 'Restriction-ligation', 'Gateway-style recombination', 'Other / specialised'],
    tooltip: 'Chemistry selection changes boundary constraints without exposing wet-lab instructions.',
    citation: {
      id: 'WP-15',
      title: 'Assembly compatibility controls',
      source: 'Internal white paper, section 7.2'
    }
  },
  {
    id: 'biosafety',
    label: 'Biosafety tier',
    value: 'Standard institutional review',
    defaultValue: 'Standard institutional review',
    options: ['Routine exempt', 'Standard institutional review', 'Enhanced review', 'External approval required'],
    tooltip: 'Biosafety tier gates the advisory acknowledgement path and audit trail.',
    citation: {
      id: 'WP-21',
      title: 'Review-tier routing',
      source: 'Internal white paper, section 8.1'
    }
  }
];

export const vectorFeatures: VectorFeature[] = [
  {
    id: 'ori',
    label: 'p15A origin',
    kind: 'origin',
    start: 120,
    end: 920,
    strand: '+',
    source: 'Backbone catalogue',
    locked: true,
    validation: 'pass'
  },
  {
    id: 'resistance',
    label: 'KanR marker',
    kind: 'resistance',
    start: 980,
    end: 1850,
    strand: '+',
    source: 'Backbone catalogue',
    locked: true,
    validation: 'pass'
  },
  {
    id: 'promoter',
    label: 'inducible promoter',
    kind: 'promoter',
    start: 2080,
    end: 2280,
    strand: '+',
    source: 'Expression defaults',
    locked: false,
    validation: 'pass'
  },
  {
    id: 'tag',
    label: 'C-terminal 6xHis',
    kind: 'tag',
    start: 3040,
    end: 3098,
    strand: '+',
    source: 'Fusion tag policy',
    locked: false,
    validation: 'pass'
  },
  {
    id: 'orf',
    label: 'cargo ORF',
    kind: 'orf',
    start: 2320,
    end: 3038,
    strand: '+',
    source: 'User cargo input',
    locked: false,
    validation: 'warn'
  },
  {
    id: 'terminator',
    label: 'terminator',
    kind: 'terminator',
    start: 3220,
    end: 3510,
    strand: '+',
    source: 'Expression defaults',
    locked: false,
    validation: 'pass'
  }
];

export const designSummary: DesignSummary = {
  designId: 'EV-2407',
  owner: 'designer.local',
  version: 'v0.3 draft',
  vectorSize: '4.2 kb',
  objective: 'Screen expression panel',
  host: 'E. coli K-12 derivative',
  reviewState: 'Pending institutional acknowledgement',
  exportReadiness: 'Blocked by review gate',
  lockedModules: 2,
  lastSaved: '2026-05-15 00:26'
};

export const workflowStages: WorkflowStage[] = [
  {
    id: 'intent',
    label: 'Intent capture',
    summary: 'Objective, host, and cargo category are defined.',
    status: 'complete',
    moduleId: 'objective'
  },
  {
    id: 'backbone',
    label: 'Backbone and cargo',
    summary: 'Backbone defaults are locked; cargo needs curator confirmation.',
    status: 'warning',
    moduleId: 'cargo'
  },
  {
    id: 'cassette',
    label: 'Expression cassette',
    summary: 'Promoter, tag, ORF, and terminator are assembled as a cassette.',
    status: 'complete',
    moduleId: 'expression'
  },
  {
    id: 'assembly',
    label: 'Assembly compatibility',
    summary: 'Golden Gate boundary annotations are internally consistent.',
    status: 'complete',
    moduleId: 'chemistry'
  },
  {
    id: 'sequence',
    label: 'Sequence validation',
    summary: 'Frame is aligned; specialised notes can trigger curator review.',
    status: 'warning',
    moduleId: 'tagging'
  },
  {
    id: 'review',
    label: 'Biosafety review',
    summary: 'Institutional acknowledgement is required before final export.',
    status: 'blocked',
    moduleId: 'biosafety'
  },
  {
    id: 'export',
    label: 'Export package',
    summary: 'Draft design bundle is available; final files remain gated.',
    status: 'pending',
    moduleId: 'biosafety'
  }
];

export const compatibilityChecks: CompatibilityCheck[] = [
  {
    id: 'compat-host-origin',
    axis: 'Host / origin',
    selection: 'E. coli K-12 derivative + p15A origin',
    status: 'pass',
    evidence: 'Replicon compatibility accepted for the selected host profile.',
    moduleId: 'host'
  },
  {
    id: 'compat-marker',
    axis: 'Host / marker',
    selection: 'KanR marker',
    status: 'pass',
    evidence: 'Selection marker is represented in the backbone catalogue.',
    moduleId: 'host'
  },
  {
    id: 'compat-expression',
    axis: 'Promoter / induction',
    selection: 'Tunable inducible expression',
    status: 'pass',
    evidence: 'Expression mode matches the selected promoter policy.',
    moduleId: 'expression'
  },
  {
    id: 'compat-cargo-tag',
    axis: 'Cargo / tag',
    selection: 'Open reading frame + C-terminal 6xHis',
    status: 'warn',
    evidence: 'Cargo boundary should be confirmed before final export.',
    moduleId: 'cargo'
  },
  {
    id: 'compat-assembly',
    axis: 'Assembly chemistry',
    selection: 'Golden Gate assembly',
    status: 'pass',
    evidence: 'Boundary annotations are internally consistent.',
    moduleId: 'chemistry'
  },
  {
    id: 'compat-review',
    axis: 'Biosafety / export',
    selection: 'Standard institutional review',
    status: 'warn',
    evidence: 'Export remains gated until the advisory decision is recorded.',
    moduleId: 'biosafety'
  }
];

export const importChannels: ImportChannel[] = [
  { id: 'sequence-file', label: 'Sequence file', value: 'GenBank / SBOL / FASTA import ready', status: 'ready' },
  { id: 'backbone', label: 'Backbone', value: 'EV-2407 p15A-KanR draft selected', status: 'locked' },
  { id: 'cargo', label: 'Cargo sequence', value: 'Open reading frame pending curator confirmation', status: 'needed' },
  { id: 'snapgene', label: 'SnapGene bridge', value: 'File-watch/API channel available after connection', status: 'ready' }
];

export const exportActions: ExportAction[] = [
  {
    id: 'validate-design',
    label: 'Validate design',
    description: 'Run construct, compatibility, citation, and advisory checks.',
    state: 'ready'
  },
  {
    id: 'draft-bundle',
    label: 'Export draft design bundle',
    description: 'Create a non-operational review package for curator inspection.',
    state: 'ready'
  },
  {
    id: 'submit-review',
    label: 'Submit for review',
    description: 'Route the current design to institutional acknowledgement.',
    state: 'queued'
  },
  {
    id: 'final-export',
    label: 'Final GenBank/SBOL/FASTA export',
    description: 'Available only after validation and advisory gates pass.',
    state: 'blocked'
  }
];

export const validationFindings: ValidationFinding[] = [
  {
    id: 'val-frame',
    moduleId: 'tagging',
    moduleLabel: 'Tagging',
    severity: 'pass',
    message: 'Fusion frame remains aligned through the tag boundary.'
  },
  {
    id: 'val-review',
    moduleId: 'biosafety',
    moduleLabel: 'Biosafety tier',
    severity: 'warn',
    message: 'Institutional review acknowledgement is required before export.'
  },
  {
    id: 'val-chemistry',
    moduleId: 'chemistry',
    moduleLabel: 'Cloning chemistry',
    severity: 'pass',
    message: 'Assembly boundary annotations are internally consistent.'
  },
  {
    id: 'val-other',
    moduleId: 'objective',
    moduleLabel: 'Objective',
    severity: 'warn',
    message: 'Specialised objective notes require curator review when populated.'
  }
];

export const advisories: Advisory[] = [
  {
    id: 'adv-biosafety',
    title: 'Institutional review gate',
    severity: 'institutional',
    moduleLabel: 'Biosafety tier',
    summary: 'This design cannot be exported until the reviewer records an acknowledge, decline, or escalate action.'
  },
  {
    id: 'adv-audit',
    title: 'Audit evidence required',
    severity: 'documentation',
    moduleLabel: 'Admin console',
    summary: 'A justification record is required for every advisory decision.'
  }
];

export const auditRecords: AuditRecord[] = [
  {
    id: 'audit-0827',
    actor: 'reviewer.local',
    action: 'Queued advisory review',
    target: 'EV-2407 inducible panel',
    timestamp: '2026-05-14 09:12'
  },
  {
    id: 'audit-0824',
    actor: 'designer.local',
    action: 'Locked module',
    target: 'p15A origin',
    timestamp: '2026-05-14 08:54'
  },
  {
    id: 'audit-0819',
    actor: 'translator.local',
    action: 'Applied constraints',
    target: 'Tunable inducible defaults',
    timestamp: '2026-05-14 08:41'
  }
];

export const reviewQueue: ReviewQueueItem[] = [
  {
    id: 'queue-11',
    designName: 'EV-2407 inducible panel',
    owner: 'designer.local',
    status: 'Pending',
    submittedAt: '2026-05-14 09:12'
  },
  {
    id: 'queue-09',
    designName: 'EV-2399 reporter cassette',
    owner: 'curator.local',
    status: 'Escalated',
    submittedAt: '2026-05-13 16:36'
  },
  {
    id: 'queue-08',
    designName: 'EV-2391 tag comparison',
    owner: 'designer.local',
    status: 'Declined',
    submittedAt: '2026-05-13 10:05'
  }
];
