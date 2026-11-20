import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { ArrowLeft, Compass, CheckCircle2, Lock, AlertCircle } from 'lucide-react';
import { getInsights, getInvestments, getDecisions } from '../api';
import { formatINR, formatPct, formatDate } from '../utils/formatters';

export function InvestmentsPage() {
  const [insights, setInsights] = useState([]);
  const [investments, setInvestments] = useState([]);
  const [decisions, setDecisions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    let isMounted = true;
    async function loadInvestmentsData() {
      setLoading(true);
      setError(null);
      try {
        const [insightsRes, investmentsRes, decisionsRes] = await Promise.all([
          getInsights(),
          getInvestments(),
          getDecisions()
        ]);

        if (isMounted) {
          setInsights(insightsRes?.insights || []);
          setInvestments(investmentsRes?.investments || []);
          setDecisions(decisionsRes?.decisions || []);
        }
      } catch (err) {
        if (isMounted) {
          setError(err.message || 'Unable to load asset records.');
        }
      } finally {
        if (isMounted) {
          setLoading(false);
        }
      }
    }

    loadInvestmentsData();
    return () => { isMounted = false; };
  }, []);

  return (
    <div className="min-h-screen bg-canvas text-ink py-8 px-4 sm:px-6">
      <div className="max-w-[720px] mx-auto space-y-8">
        {/* Navigation Header */}
        <div>
          <Link
            to="/"
            className="inline-flex items-center text-xs font-mono text-ink-muted hover:text-ink transition-colors"
          >
            <ArrowLeft className="w-3.5 h-3.5 mr-1.5" />
            Back to thinking companion
          </Link>
        </div>

        {error && (
          <div className="p-4 rounded-xl bg-red-950/30 border border-red-800/40 text-red-300 text-xs font-mono flex items-center space-x-2">
            <AlertCircle className="w-4 h-4 flex-shrink-0" />
            <span>{error}</span>
          </div>
        )}

        {/* Top: Your Patterns */}
        <section className="space-y-3">
          <div className="flex items-center space-x-2 pb-1 border-b border-canvas-border">
            <Compass className="w-4 h-4 text-accent" />
            <h2 className="font-mono text-xs uppercase tracking-wider text-ink font-medium">
              Your patterns
            </h2>
          </div>

          {loading ? (
            <div className="p-4 text-xs font-mono text-ink-muted bg-canvas-card border border-canvas-border rounded-lg text-center">
              Analyzing decision patterns...
            </div>
          ) : insights.length === 0 ? (
            <div className="p-4 text-xs font-mono text-ink-faint bg-canvas-card border border-canvas-border rounded-lg text-center">
              No behavioral patterns identified yet.
            </div>
          ) : (
            <div className="space-y-2.5">
              {insights.map((ins) => (
                <div
                  key={ins.id}
                  className="p-3.5 rounded-lg bg-canvas-card border-l-2 border-l-accent border border-canvas-border text-xs flex items-start justify-between gap-4"
                >
                  <p className="text-ink leading-relaxed">{ins.text}</p>
                  {ins.evidence_count && (
                    <span className="font-mono text-[10px] text-ink-muted flex-shrink-0 bg-canvas-hover px-2 py-0.5 rounded border border-canvas-border">
                      {ins.evidence_count} events
                    </span>
                  )}
                </div>
              ))}
            </div>
          )}
        </section>

        {/* Middle: Asset Holdings */}
        <section className="space-y-3">
          <div className="flex items-center justify-between pb-1 border-b border-canvas-border">
            <h2 className="font-mono text-xs uppercase tracking-wider text-ink font-medium">
              Recorded Asset Holdings
            </h2>
            <span className="font-mono text-[11px] text-ink-muted">
              {investments.length} tracked
            </span>
          </div>

          {loading ? (
            <div className="p-8 text-center text-xs font-mono text-ink-muted bg-canvas-card border border-canvas-border rounded-lg">
              Retrieving asset records...
            </div>
          ) : investments.length === 0 ? (
            <div className="p-8 text-center text-xs font-mono text-ink-muted bg-canvas-card border border-canvas-border rounded-lg leading-relaxed">
              Nothing recorded yet. Tell me what you've bought in the chat.
            </div>
          ) : (
            <div className="space-y-3">
              {investments.map((inv) => (
                <div
                  key={inv.id}
                  className="p-4 rounded-xl bg-canvas-card border border-canvas-border hover:border-canvas-borderLight transition-colors text-xs font-mono"
                >
                  <div className="flex items-center justify-between pb-2 mb-2 border-b border-canvas-border">
                    <div className="flex items-center space-x-2">
                      <span className="text-sm font-medium text-ink">{inv.stock_name || inv.ticker}</span>
                      <span className="text-[10px] text-ink-muted bg-canvas-hover px-1.5 py-0.5 rounded border border-canvas-border">
                        {inv.ticker}
                      </span>
                    </div>

                    <div className="text-ink font-medium">
                      {inv.current_value !== null ? formatINR(inv.current_value) : '—'}
                    </div>
                  </div>

                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 text-ink-muted text-[11px]">
                    <div>
                      <span className="text-[10px] text-ink-faint block uppercase">Quantity</span>
                      <span className="text-ink mt-0.5 block">{inv.quantity}</span>
                    </div>
                    <div>
                      <span className="text-[10px] text-ink-faint block uppercase">Avg Price</span>
                      <span className="text-ink mt-0.5 block">{formatINR(inv.avg_price)}</span>
                    </div>
                    <div>
                      <span className="text-[10px] text-ink-faint block uppercase">Acquired</span>
                      <span className="text-ink mt-0.5 block">{formatDate(inv.purchase_date)}</span>
                    </div>
                    <div>
                      <span className="text-[10px] text-ink-faint block uppercase">Linked Tip</span>
                      <span className="text-ink mt-0.5 block">{inv.linked_tip_id ? `#${inv.linked_tip_id}` : '—'}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </section>

        {/* Bottom: Past Decisions */}
        <section className="space-y-3">
          <div className="flex items-center space-x-2 pb-1 border-b border-canvas-border">
            <Lock className="w-4 h-4 text-accent" />
            <h2 className="font-mono text-xs uppercase tracking-wider text-ink font-medium">
              Past Locked Decisions
            </h2>
          </div>

          {loading ? (
            <div className="p-8 text-center text-xs font-mono text-ink-muted bg-canvas-card border border-canvas-border rounded-lg">
              Retrieving decisions...
            </div>
          ) : decisions.length === 0 ? (
            <div className="p-8 text-center text-xs font-mono text-ink-faint bg-canvas-card border border-canvas-border rounded-lg">
              No locked decisions recorded.
            </div>
          ) : (
            <div className="space-y-3">
              {decisions.map((dec) => {
                const actionLabels = {
                  bought: 'Bought',
                  skipped: 'Skipped',
                  watching: 'Watching'
                };

                return (
                  <div
                    key={dec.id}
                    className="p-4 rounded-xl bg-canvas-card border border-canvas-border hover:border-canvas-borderLight transition-colors text-xs"
                  >
                    <div className="flex items-center justify-between pb-2 mb-2 border-b border-canvas-border">
                      <div className="flex items-center space-x-2">
                        <span className="font-medium text-ink">
                          {dec.stock?.name || dec.stock?.ticker || 'Security'}
                        </span>
                        {dec.source_name && (
                          <span className="font-mono text-[10px] text-ink-muted bg-canvas-hover px-1.5 py-0.5 rounded border border-canvas-border">
                            via {dec.source_name}
                          </span>
                        )}
                      </div>

                      <div className="flex items-center space-x-2">
                        <span className="font-mono text-[10px] uppercase px-2 py-0.5 rounded bg-canvas-hover border border-canvas-border text-ink font-medium">
                          {actionLabels[dec.action] || dec.action}
                        </span>
                        <span className="font-mono text-[10px] text-ink-muted">
                          {formatDate(dec.locked_at)}
                        </span>
                      </div>
                    </div>

                    {dec.thesis && (
                      <p className="text-ink-muted text-xs mb-3 italic">
                        &ldquo;{dec.thesis}&rdquo;
                      </p>
                    )}

                    <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 font-mono text-[11px]">
                      <div className="p-1.5 rounded bg-canvas-hover border border-canvas-border">
                        <span className="text-[10px] text-ink-muted uppercase block">Timeframe</span>
                        <span className="text-ink mt-0.5 block">{dec.timeframe_days}d</span>
                      </div>
                      <div className="p-1.5 rounded bg-canvas-hover border border-canvas-border">
                        <span className="text-[10px] text-ink-muted uppercase block">Target Price</span>
                        <span className="text-ink mt-0.5 block">{formatINR(dec.exit_target)}</span>
                      </div>
                      <div className="p-1.5 rounded bg-canvas-hover border border-canvas-border">
                        <span className="text-[10px] text-ink-muted uppercase block">Risk Limit</span>
                        <span className="text-ink mt-0.5 block">{formatPct(dec.max_loss_pct, false)}</span>
                      </div>
                      <div className="p-1.5 rounded bg-canvas-hover border border-canvas-border">
                        <span className="text-[10px] text-ink-muted uppercase block">Confidence</span>
                        <span className="text-ink mt-0.5 block">{dec.confidence} / 5</span>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </section>
      </div>
    </div>
  );
}

export default InvestmentsPage;
