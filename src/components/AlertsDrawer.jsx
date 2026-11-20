import React, { useEffect } from 'react';
import { X, CheckCheck, CheckCircle2, AlertOctagon, Info } from 'lucide-react';
import { useAlerts } from '../context/AlertsContext';
import { formatRelativeTime, formatPct } from '../utils/formatters';

export function AlertsDrawer() {
  const {
    drawerOpen,
    setDrawerOpen,
    alerts,
    unreadCount,
    loading,
    markSingleRead,
    markAllRead
  } = useAlerts();

  // Close on ESC
  useEffect(() => {
    function handleKeyDown(e) {
      if (e.key === 'Escape') {
        setDrawerOpen(false);
      }
    }
    if (drawerOpen) {
      window.addEventListener('keydown', handleKeyDown);
    }
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [drawerOpen, setDrawerOpen]);

  if (!drawerOpen) return null;

  const typeConfig = {
    outcome_confirmed: {
      icon: CheckCircle2,
      iconColor: 'text-accent',
      badgeColor: 'bg-accent/10 text-accent border-accent/30',
      label: 'Outcome Confirmed'
    },
    negative_outcome: {
      icon: AlertOctagon,
      iconColor: 'text-status-no_evidence',
      badgeColor: 'bg-red-950/30 text-red-400 border-red-800/40',
      label: 'Negative Outcome'
    },
    new_update: {
      icon: Info,
      iconColor: 'text-amber-400',
      badgeColor: 'bg-amber-950/30 text-amber-300 border-amber-800/40',
      label: 'Pattern Update'
    }
  };

  const renderHorizonResult = (label, result) => {
    if (!result || result.status === 'pending') {
      return (
        <div className="flex flex-col items-center p-1.5 rounded bg-canvas-hover border border-canvas-border text-[11px] font-mono">
          <span className="text-[10px] text-ink-muted uppercase">{label}</span>
          <span className="text-ink-faint mt-0.5">—</span>
        </div>
      );
    }

    const isWorked = result.status === 'worked';
    const returnText = formatPct(result.return_pct);
    const benchText = formatPct(result.benchmark_pct);

    return (
      <div className="flex flex-col items-center p-1.5 rounded bg-canvas-hover border border-canvas-border text-[11px] font-mono">
        <span className="text-[10px] text-ink-muted uppercase">{label}</span>
        <span className={`font-medium mt-0.5 ${isWorked ? 'text-accent' : 'text-status-no_evidence'}`}>
          {returnText}
        </span>
        <span className="text-[9px] text-ink-faint">
          vs {benchText}
        </span>
      </div>
    );
  };

  return (
    <div className="fixed inset-0 z-50 flex justify-end">
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-black/60 backdrop-blur-xs transition-opacity"
        onClick={() => setDrawerOpen(false)}
        aria-hidden="true"
      />

      {/* Drawer */}
      <div className="relative w-full max-w-md bg-canvas border-l border-canvas-border h-full shadow-2xl flex flex-col z-10 animate-slideIn">
        {/* Header */}
        <div className="p-4 border-b border-canvas-border flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <span className="font-mono text-sm uppercase tracking-wider text-ink font-medium">
              Alerts & Horizons
            </span>
            {unreadCount > 0 && (
              <span className="px-2 py-0.5 rounded-full text-[10px] font-mono bg-accent/15 text-accent border border-accent/30 font-medium">
                {unreadCount} new
              </span>
            )}
          </div>

          <div className="flex items-center space-x-2">
            {unreadCount > 0 && (
              <button
                type="button"
                onClick={markAllRead}
                className="px-2 py-1 text-[11px] font-mono text-ink-muted hover:text-ink hover:bg-canvas-hover rounded flex items-center transition-colors"
                title="Mark all read"
              >
                <CheckCheck className="w-3.5 h-3.5 mr-1 text-accent" />
                Mark all read
              </button>
            )}

            <button
              type="button"
              onClick={() => setDrawerOpen(false)}
              className="p-1.5 rounded-lg text-ink-muted hover:text-ink hover:bg-canvas-hover transition-colors"
              aria-label="Close alerts drawer"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Alerts List */}
        <div className="flex-1 overflow-y-auto p-4 space-y-3">
          {loading && alerts.length === 0 ? (
            <div className="p-8 text-center text-xs font-mono text-ink-muted">
              Loading alerts...
            </div>
          ) : alerts.length === 0 ? (
            <div className="p-8 text-center text-xs font-mono text-ink-faint">
              No alerts recorded yet.
            </div>
          ) : (
            alerts.map((alert) => {
              const cfg = typeConfig[alert.type] || typeConfig.new_update;
              const Icon = cfg.icon;

              return (
                <div
                  key={alert.id}
                  onClick={() => !alert.read && markSingleRead(alert.id)}
                  className={`p-3.5 rounded-lg border transition-all cursor-pointer ${
                    alert.read
                      ? 'bg-canvas-card border-canvas-border opacity-85 hover:opacity-100'
                      : 'bg-canvas-card border-canvas-borderLight ring-1 ring-accent/20'
                  }`}
                >
                  <div className="flex items-start justify-between gap-2 mb-2">
                    <div className="flex items-center space-x-2">
                      <Icon className={`w-4 h-4 flex-shrink-0 ${cfg.iconColor}`} />
                      <span className="font-medium text-xs text-ink">
                        {alert.title}
                      </span>
                    </div>

                    <div className="flex items-center space-x-1.5 flex-shrink-0">
                      <span className="text-[10px] font-mono text-ink-faint">
                        {formatRelativeTime(alert.created_at)}
                      </span>
                      {!alert.read && (
                        <span className="w-1.5 h-1.5 rounded-full bg-accent" title="Unread" />
                      )}
                    </div>
                  </div>

                  <p className="text-xs text-ink-muted mb-2.5 leading-relaxed">
                    {alert.body}
                  </p>

                  {alert.source_name && (
                    <div className="text-[10px] font-mono text-ink-faint mb-2.5">
                      Source: <span className="text-ink-muted">{alert.source_name}</span>
                    </div>
                  )}

                  {/* Horizon Results */}
                  {alert.results && (
                    <div className="grid grid-cols-3 gap-2 pt-2 border-t border-canvas-border">
                      {renderHorizonResult('d7', alert.results.d7)}
                      {renderHorizonResult('d30', alert.results.d30)}
                      {renderHorizonResult('d90', alert.results.d90)}
                    </div>
                  )}
                </div>
              );
            })
          )}
        </div>
      </div>
    </div>
  );
}

export default AlertsDrawer;
