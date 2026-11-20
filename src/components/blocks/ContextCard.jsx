import React from 'react';
import { TrendingUp, TrendingDown, Info } from 'lucide-react';
import { formatINR, formatPct } from '../../utils/formatters';

export function ContextCard({ block }) {
  const { ticker, price_now, change_7d_pct, since_tip_pct, note } = block || {};
  const is7dPositive = change_7d_pct >= 0;

  return (
    <div className="w-full bg-canvas-card border border-canvas-border rounded-lg p-3.5 my-2 text-xs">
      <div className="flex items-center justify-between pb-2 mb-2 border-b border-canvas-border">
        <div className="flex items-center space-x-2">
          <span className="font-mono text-[11px] uppercase tracking-wider text-ink-muted">Market Context</span>
          <span className="font-mono font-medium text-ink bg-canvas-hover px-1.5 py-0.5 rounded border border-canvas-border">
            {ticker}
          </span>
        </div>
        <div className="font-mono font-medium text-ink text-sm">
          {formatINR(price_now)}
        </div>
      </div>

      <div className="flex flex-wrap items-center gap-3 my-2">
        <div className="flex items-center space-x-1.5">
          <span className="text-ink-muted">7d Change:</span>
          <span className={`inline-flex items-center font-mono font-medium ${is7dPositive ? 'text-accent' : 'text-status-no_evidence'}`}>
            {is7dPositive ? <TrendingUp className="w-3 h-3 mr-0.5" /> : <TrendingDown className="w-3 h-3 mr-0.5" />}
            {formatPct(change_7d_pct)}
          </span>
        </div>

        {since_tip_pct !== null && since_tip_pct !== undefined && (
          <div className="flex items-center space-x-1.5">
            <span className="text-ink-muted">Since Tip:</span>
            <span className={`inline-flex items-center font-mono font-medium ${since_tip_pct >= 0 ? 'text-accent' : 'text-status-no_evidence'}`}>
              {formatPct(since_tip_pct)}
            </span>
          </div>
        )}
      </div>

      {note && (
        <div className="flex items-start space-x-1.5 text-ink-muted mt-2 pt-2 border-t border-canvas-border text-[11px] leading-relaxed">
          <Info className="w-3.5 h-3.5 flex-shrink-0 text-ink-faint mt-0.5" />
          <span>{note}</span>
        </div>
      )}
    </div>
  );
}

export default ContextCard;
