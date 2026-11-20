import React from 'react';
import { AlertTriangle, Tag } from 'lucide-react';
import { humanizeTag } from '../../utils/formatters';

export function ClaimCard({ block }) {
  const { sender, stock, claim, red_flags = [] } = block || {};

  return (
    <div className="w-full bg-canvas-card border border-canvas-border rounded-lg p-4 my-2 text-sm">
      <div className="flex items-center justify-between pb-2 mb-2 border-b border-canvas-border">
        <div className="flex items-center space-x-2">
          <span className="font-mono text-xs uppercase tracking-wider text-ink-muted">Claim Forwarded</span>
          {sender && (
            <span className="font-mono text-xs text-ink px-1.5 py-0.5 bg-canvas-hover rounded border border-canvas-border">
              via {sender}
            </span>
          )}
        </div>
        {stock?.ticker && (
          <span className="font-mono text-xs font-medium text-ink bg-canvas-hover px-2 py-0.5 rounded border border-canvas-border">
            {stock.ticker}
          </span>
        )}
      </div>

      <div className="mb-2">
        <div className="text-xs text-ink-muted mb-0.5">{stock?.name || 'Asset'}</div>
        <div className="text-sm text-ink font-medium leading-relaxed">
          &ldquo;{claim}&rdquo;
        </div>
      </div>

      {red_flags.length > 0 && (
        <div className="mt-3 pt-2 border-t border-canvas-border flex flex-wrap items-center gap-1.5">
          <span className="flex items-center text-[10px] font-mono text-status-unchecked uppercase tracking-wider mr-1">
            <AlertTriangle className="w-3 h-3 mr-1" />
            Flags:
          </span>
          {red_flags.map((flag, idx) => (
            <span
              key={idx}
              className="inline-flex items-center text-[10px] font-mono uppercase px-1.5 py-0.5 rounded bg-amber-950/30 text-amber-300 border border-amber-800/50"
            >
              {humanizeTag(flag)}
            </span>
          ))}
        </div>
      )}
    </div>
  );
}

export default ClaimCard;
