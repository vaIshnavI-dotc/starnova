import React from 'react';
import { UserCheck } from 'lucide-react';

export function SourceChip({ block }) {
  const {
    source_name = 'Source',
    tips_total = 0,
    tips_worked = 0,
    shrunk_hit_rate,
    evidence_level,
    label
  } = block || {};

  const evidenceLevelColors = {
    none: 'text-ink-faint border-canvas-border',
    low: 'text-amber-400 border-amber-800/40 bg-amber-950/20',
    medium: 'text-ink-muted border-canvas-borderLight bg-canvas-hover',
    high: 'text-accent border-accent/30 bg-accent/10'
  };

  const levelColor = evidenceLevelColors[evidence_level] || evidenceLevelColors.none;

  return (
    <div className="inline-flex flex-wrap items-center gap-2 px-3 py-1.5 my-1.5 bg-canvas-card border border-canvas-border rounded-full text-xs">
      <div className="flex items-center text-ink-muted">
        <UserCheck className="w-3.5 h-3.5 mr-1.5 text-accent" />
        <span className="font-mono text-ink">
          {source_name}: {tips_worked} of {tips_total} tips worked
        </span>
      </div>

      {shrunk_hit_rate !== undefined && (
        <span className="font-mono text-[11px] text-ink-muted">
          ({Math.round(shrunk_hit_rate * 100)}% adj.)
        </span>
      )}

      {label && (
        <span className="px-2 py-0.5 rounded-full text-[10px] font-mono bg-canvas-hover border border-canvas-border text-ink">
          {label}
        </span>
      )}

      {evidence_level && (
        <span className={`px-2 py-0.5 rounded-full text-[10px] font-mono uppercase tracking-wider border ${levelColor}`}>
          ev: {evidence_level}
        </span>
      )}
    </div>
  );
}

export default SourceChip;
