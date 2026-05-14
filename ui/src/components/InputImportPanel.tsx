import { Database, Dna, FileUp, Link2 } from 'lucide-react';
import type { ImportChannel } from '../types';

const channelIcon = {
  'sequence-file': FileUp,
  backbone: Database,
  cargo: Dna,
  snapgene: Link2
};

type InputImportPanelProps = {
  channels: ImportChannel[];
};

export function InputImportPanel({ channels }: InputImportPanelProps) {
  return (
    <section className="panel input-panel" aria-labelledby="input-heading">
      <div className="panel-header compact">
        <div>
          <p className="eyebrow">Inputs</p>
          <h2 id="input-heading">Import and selection</h2>
        </div>
      </div>

      <div className="input-channel-list">
        {channels.map((channel) => {
          const Icon = channelIcon[channel.id as keyof typeof channelIcon] ?? FileUp;

          return (
            <article key={channel.id} className={`input-channel ${channel.status}`}>
              <Icon size={18} />
              <div>
                <h3>{channel.label}</h3>
                <p>{channel.value}</p>
              </div>
              <span>{channel.status}</span>
            </article>
          );
        })}
      </div>

      <div className="input-actions" aria-label="Input actions">
        <button type="button">Import sequence</button>
        <button type="button">Select backbone</button>
        <button type="button">Paste cargo</button>
      </div>
    </section>
  );
}
