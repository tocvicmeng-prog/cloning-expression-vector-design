import { Minus, Plus, ScanSearch } from 'lucide-react';
import type { VectorFeature } from '../types';

const featureColors: Record<VectorFeature['kind'], string> = {
  promoter: '#2f7d32',
  orf: '#355c9a',
  tag: '#7f5a00',
  terminator: '#246a73',
  resistance: '#b24b35',
  origin: '#5d6b78'
};

type VectorWorkspaceProps = {
  features: VectorFeature[];
  zoom: number;
  onZoomChange: (zoom: number) => void;
};

function polarToCartesian(center: number, radius: number, angleInDegrees: number) {
  const angleInRadians = ((angleInDegrees - 90) * Math.PI) / 180.0;
  return {
    x: center + radius * Math.cos(angleInRadians),
    y: center + radius * Math.sin(angleInRadians)
  };
}

function featureArc(feature: VectorFeature, totalLength: number) {
  const radius = 92;
  const center = 125;
  const startAngle = (feature.start / totalLength) * 360;
  const endAngle = (feature.end / totalLength) * 360;
  const start = polarToCartesian(center, radius, endAngle);
  const end = polarToCartesian(center, radius, startAngle);
  const largeArcFlag = endAngle - startAngle <= 180 ? '0' : '1';

  return `M ${start.x} ${start.y} A ${radius} ${radius} 0 ${largeArcFlag} 0 ${end.x} ${end.y}`;
}

export function VectorWorkspace({ features, zoom, onZoomChange }: VectorWorkspaceProps) {
  const totalLength = 4200;
  const linearScale = zoom / totalLength;

  return (
    <section className="panel vector-panel" aria-labelledby="vector-heading">
      <div className="panel-header compact">
        <div>
          <p className="eyebrow">Maps</p>
          <h2 id="vector-heading">Vector map</h2>
        </div>
        <div className="segmented-control" aria-label="Map zoom">
          <button
            type="button"
            title="Zoom out"
            aria-label="Zoom out"
            onClick={() => onZoomChange(Math.max(2800, zoom - 400))}
          >
            <Minus size={16} />
          </button>
          <output aria-label="Current zoom">{zoom} bp</output>
          <button
            type="button"
            title="Zoom in"
            aria-label="Zoom in"
            onClick={() => onZoomChange(Math.min(6000, zoom + 400))}
          >
            <Plus size={16} />
          </button>
        </div>
      </div>

      <div className="map-layout">
        <figure className="plasmid-map" aria-label="Circular plasmid map">
          <svg viewBox="0 0 250 250" role="img" aria-labelledby="plasmid-title">
            <title id="plasmid-title">Circular plasmid map</title>
            <circle cx="125" cy="125" r="92" fill="none" stroke="#d7dee6" strokeWidth="18" />
            {features.map((feature) => (
              <path
                key={feature.id}
                d={featureArc(feature, totalLength)}
                fill="none"
                stroke={featureColors[feature.kind]}
                strokeWidth="16"
                strokeLinecap="round"
              />
            ))}
            <circle cx="125" cy="125" r="54" fill="#f8fafc" stroke="#d7dee6" />
            <text x="125" y="119" textAnchor="middle" className="map-title">
              EV-2407
            </text>
            <text x="125" y="139" textAnchor="middle" className="map-subtitle">
              4.2 kb
            </text>
          </svg>
        </figure>

        <div className="linear-map" aria-label="Linear feature map">
          <div className="linear-toolbar">
            <ScanSearch size={16} />
            <span>Linear feature map</span>
          </div>
          <div className="linear-scroll" role="region" aria-label="Scrollable feature map" tabIndex={0}>
            <div className="linear-track" style={{ width: `${zoom}px` }}>
              {features.map((feature) => {
                const left = feature.start * linearScale;
                const width = Math.max(72, (feature.end - feature.start) * linearScale);

                return (
                  <span
                    key={feature.id}
                    className={`feature-block ${feature.kind}`}
                    style={{ left: `${left}px`, width: `${width}px` }}
                    title={`${feature.label}: ${feature.start}-${feature.end}`}
                  >
                    {feature.locked ? 'Lock ' : ''}
                    {feature.label}
                  </span>
                );
              })}
            </div>
          </div>
        </div>
      </div>

      <div className="translation-panel" aria-label="ORF translation frames">
        {['Frame +1', 'Frame +2', 'Frame +3'].map((frame, index) => (
          <div key={frame} className="translation-row">
            <span>{frame}</span>
            <code>
              {index === 0 ? (
                <>
                  <mark className="start">ATG</mark> GCT ACC GAA TCC GGT <mark className="fusion">CAT CAC</mark>{' '}
                  <mark className="stop">TAA</mark>
                </>
              ) : (
                <>TGC TAC CGA ATC CGG TCA TCA CTA A</>
              )}
            </code>
          </div>
        ))}
      </div>
    </section>
  );
}
