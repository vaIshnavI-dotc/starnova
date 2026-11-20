import React, { useState } from 'react';
import { ChevronDown, ChevronRight, ExternalLink, ShieldCheck, AlertCircle, XCircle } from 'lucide-react';

export function ThesisChain({ block }) {
  const { links = [], gaps_count = 0, total_links = 0, summary } = block || {};
  const [expandedIds, setExpandedIds] = useState(() => {
    // Default open backed links that have evidence
    const initial = {};
    links.forEach(l => {
      if (l.evidence?.summary) initial[l.id] = true;
    });
    return initial;
  });

  const toggleLink = (id) => {
    setExpandedIds(prev => ({ ...prev, [id]: !prev[id] }));
  };

  const statusConfig = {
    backed: {
      label: 'BACKED',
      badgeClass: 'text-accent bg-accent/10 border-accent/30',
      icon: ShieldCheck,
      dotClass: 'bg-accent'
    },
    unchecked: {
      label: 'UNCHECKED',
      badgeClass: 'text-amber-400 bg-amber-950/30 border-amber-800/40',
      icon: AlertCircle,
      dotClass: 'bg-amber-400'
    },
    no_evidence: {
      label: 'NO EVIDENCE',
      badgeClass: 'text-red-400 bg-red-950/30 border-red-800/40',
      icon: XCircle,
      dotClass: 'bg-red-400'
    }
  };

  return (
    <div className="w-full bg-canvas-card border border-canvas-border rounded-lg p-4 my-2.5 text-xs">
      <div className="flex items-center justify-between pb-3 mb-3 border-b border-canvas-border">
        <span className="font-mono text-xs uppercase tracking-wider text-ink-muted">
          Thesis Verification Chain
        </span>
        <span className="font-mono text-[11px] text-ink-muted">
          {total_links - gaps_count}/{total_links} verified
        </span>
      </div>

      <div className="relative pl-3 space-y-4">
        {links.map((link, idx) => {
          const cfg = statusConfig[link.status] || statusConfig.unchecked;
          const StatusIcon = cfg.icon;
          const isExpanded = !!expandedIds[link.id];
          const hasEvidence = Boolean(link.evidence?.summary);
          const isLast = idx === links.length - 1;

          return (
            <div key={link.id || idx} className="relative group">
              {/* Vertical connector line */}
              {!isLast && (
                <div
                  className="absolute left-[7px] top-6 bottom-[-16px] w-[2px] bg-canvas-border group-hover:bg-canvas-borderLight transition-colors"
                  aria-hidden="true"
                />
              )}

              <div className="flex items-start space-x-3">
                {/* Node indicator */}
                <div className={`w-4 h-4 rounded-full mt-0.5 flex-shrink-0 flex items-center justify-center border border-canvas ${cfg.dotClass}`}>
                  <div className="w-1.5 h-1.5 rounded-full bg-canvas" />
                </div>

                <div className="flex-1 min-w-0">
                  <div className="flex items-start justify-between gap-2">
                    <span className="text-sm text-ink leading-snug font-normal">
                      {link.text}
                    </span>
                    <span
                      className={`inline-flex items-center text-[10px] font-mono px-2 py-0.5 rounded border flex-shrink-0 ${cfg.badgeClass}`}
                    >
                      <StatusIcon className="w-2.5 h-2.5 mr-1" />
                      {cfg.label}
                    </span>
                  </div>

                  {/* Expandable evidence section */}
                  {hasEvidence && (
                    <div className="mt-1.5">
                      <button
                        type="button"
                        onClick={() => toggleLink(link.id)}
                        className="inline-flex items-center text-[11px] font-mono text-ink-muted hover:text-ink transition-colors focus:outline-none"
                      >
                        {isExpanded ? (
                          <ChevronDown className="w-3.5 h-3.5 mr-1 text-ink-faint" />
                        ) : (
                          <ChevronRight className="w-3.5 h-3.5 mr-1 text-ink-faint" />
                        )}
                        {isExpanded ? 'Hide evidence' : 'View evidence'}
                      </button>

                      {isExpanded && (
                        <div className="mt-1.5 p-2.5 rounded bg-canvas-hover border border-canvas-border text-[11px] text-ink-muted space-y-1.5 animate-fade">
                          <p className="leading-relaxed">{link.evidence.summary}</p>
                          {link.evidence.source_url && (
                            <a
                              href={link.evidence.source_url}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="inline-flex items-center font-mono text-[10px] text-accent hover:underline"
                            >
                              <ExternalLink className="w-3 h-3 mr-1" />
                              Source Reference
                            </a>
                          )}
                        </div>
                      )}
                    </div>
                  )}
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Summary Footer */}
      <div className="mt-4 pt-3 border-t border-canvas-border flex items-center justify-between">
        <span className="text-xs text-ink-muted font-mono">
          {summary || `${gaps_count} of ${total_links} links have no evidence.`}
        </span>
        <div className="flex items-center space-x-1">
          {Array.from({ length: total_links }).map((_, i) => (
            <div
              key={i}
              className={`w-1.5 h-1.5 rounded-full ${i < (total_links - gaps_count) ? 'bg-accent' : 'bg-red-400'}`}
            />
          ))}
        </div>
      </div>
    </div>
  );
}

export default ThesisChain;
