import React, { useState } from 'react';
import { Lock, CheckCircle2, AlertCircle } from 'lucide-react';
import { lockDecision } from '../../api';
import { formatINR, formatPct, formatDate } from '../../utils/formatters';

export function DecisionGate({ block, onDecisionLocked }) {
  const {
    decision_id = 'd_1',
    values = {},
    locked: initialLocked = false,
    locked_at: initialLockedAt = null
  } = block || {};

  const [locked, setLocked] = useState(initialLocked);
  const [lockedData, setLockedData] = useState(initialLocked ? { ...values, locked_at: initialLockedAt } : null);

  const [action, setAction] = useState(values.action || '');
  const [timeframeDays, setTimeframeDays] = useState(values.timeframe_days || '');
  const [exitTarget, setExitTarget] = useState(values.exit_target || '');
  const [maxLossPct, setMaxLossPct] = useState(values.max_loss_pct || '');
  const [confidence, setConfidence] = useState(values.confidence || null);

  const [submitting, setSubmitting] = useState(false);
  const [serverError, setServerError] = useState(null);
  const [missingFields, setMissingFields] = useState([]);

  // Client-side validation per contract
  const isTimeframeValid = timeframeDays !== '' && Number.isInteger(Number(timeframeDays)) && Number(timeframeDays) > 0;
  const isExitTargetValid = exitTarget !== '' && !isNaN(Number(exitTarget)) && Number(exitTarget) > 0;
  const isMaxLossValid = maxLossPct !== '' && !isNaN(Number(maxLossPct)) && Number(maxLossPct) > 0 && Number(maxLossPct) <= 100;
  const isConfidenceValid = confidence !== null && [1, 2, 3, 4, 5].includes(Number(confidence));
  const isActionValid = ['bought', 'skipped', 'watching'].includes(action);

  const isFormValid = isActionValid && isTimeframeValid && isExitTargetValid && isMaxLossValid && isConfidenceValid;

  const handleLock = async (e) => {
    e.preventDefault();
    if (!isFormValid || submitting) return;

    setSubmitting(true);
    setServerError(null);
    setMissingFields([]);

    try {
      const res = await lockDecision({
        decision_id,
        action,
        timeframe_days: parseInt(timeframeDays, 10),
        exit_target: parseFloat(exitTarget),
        max_loss_pct: parseFloat(maxLossPct),
        confidence: parseInt(confidence, 10)
      });

      if (res?.decision) {
        setLocked(true);
        setLockedData(res.decision);
        if (onDecisionLocked) {
          onDecisionLocked(res.decision);
        }
      }
    } catch (err) {
      if (err.code === 'gate_incomplete' && err.details?.missing_fields) {
        setMissingFields(err.details.missing_fields);
        setServerError('Please complete all highlighted fields before locking.');
      } else {
        setServerError(err.message || 'Failed to lock decision.');
      }
    } finally {
      setSubmitting(false);
    }
  };

  // Render collapsed read-only summary after locking
  if (locked) {
    const data = lockedData || values;
    const actionLabels = {
      bought: 'Action: Bought',
      skipped: 'Action: Skipped',
      watching: 'Action: Watching'
    };

    return (
      <div className="w-full bg-canvas-card border border-canvas-border rounded-lg p-4 my-3 text-xs animate-fade">
        <div className="flex items-center justify-between pb-2 mb-3 border-b border-canvas-border">
          <div className="flex items-center space-x-2 text-accent">
            <CheckCircle2 className="w-4 h-4" />
            <span className="font-mono text-xs uppercase tracking-wider font-medium">
              Decision Gate Locked
            </span>
          </div>
          <span className="font-mono text-[11px] text-ink-muted">
            {formatDate(data.locked_at || initialLockedAt || new Date().toISOString())}
          </span>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5">
          <div className="p-2 rounded bg-canvas-hover border border-canvas-border">
            <div className="text-ink-muted text-[10px] font-mono uppercase">Action</div>
            <div className="font-mono text-xs font-medium text-ink mt-0.5">
              {actionLabels[data.action] || data.action || 'Recorded'}
            </div>
          </div>
          <div className="p-2 rounded bg-canvas-hover border border-canvas-border">
            <div className="text-ink-muted text-[10px] font-mono uppercase">Timeframe</div>
            <div className="font-mono text-xs font-medium text-ink mt-0.5">
              {data.timeframe_days} days
            </div>
          </div>
          <div className="p-2 rounded bg-canvas-hover border border-canvas-border">
            <div className="text-ink-muted text-[10px] font-mono uppercase">Exit Target</div>
            <div className="font-mono text-xs font-medium text-ink mt-0.5">
              {formatINR(data.exit_target)}
            </div>
          </div>
          <div className="p-2 rounded bg-canvas-hover border border-canvas-border">
            <div className="text-ink-muted text-[10px] font-mono uppercase">Risk Limit</div>
            <div className="font-mono text-xs font-medium text-ink mt-0.5">
              {formatPct(data.max_loss_pct, false)}
            </div>
          </div>
        </div>

        <div className="mt-3 pt-2 border-t border-canvas-border flex items-center justify-between text-[11px] text-ink-muted">
          <span>Confidence score: <strong className="font-mono text-ink">{data.confidence} / 5</strong></span>
          <span className="font-mono text-[10px] text-ink-faint">Recorded for outcome evaluation</span>
        </div>
      </div>
    );
  }

  // Active Interactive Decision Gate Card
  return (
    <div className="w-full bg-canvas-card border border-canvas-border rounded-lg p-4 my-3 text-xs">
      <div className="flex items-center justify-between pb-2 mb-3 border-b border-canvas-border">
        <div className="flex items-center space-x-2 text-ink">
          <Lock className="w-3.5 h-3.5 text-accent" />
          <span className="font-mono text-xs uppercase tracking-wider font-medium">
            Decision Gate
          </span>
        </div>
        <span className="text-[11px] text-ink-muted font-mono">
          All criteria required
        </span>
      </div>

      {serverError && (
        <div className="mb-3 p-2 rounded bg-red-950/30 border border-red-800/40 text-red-300 text-xs flex items-center space-x-1.5">
          <AlertCircle className="w-4 h-4 flex-shrink-0" />
          <span>{serverError}</span>
        </div>
      )}

      <form onSubmit={handleLock} className="space-y-3.5">
        {/* Segmented Control for Action: Bought / Skipped / Watching */}
        <div>
          <label className="block text-[11px] font-mono uppercase text-ink-muted mb-1.5">
            Action Recorded
          </label>
          <div className={`grid grid-cols-3 gap-1 p-1 bg-canvas-subtle border rounded-md ${missingFields.includes('action') ? 'border-red-500' : 'border-canvas-border'}`}>
            {[
              { id: 'bought', label: 'Bought' },
              { id: 'skipped', label: 'Skipped' },
              { id: 'watching', label: 'Watching' }
            ].map((opt) => (
              <button
                key={opt.id}
                type="button"
                onClick={() => setAction(opt.id)}
                className={`py-1.5 text-xs font-medium rounded transition-colors text-center ${
                  action === opt.id
                    ? 'bg-canvas-hover text-ink shadow border border-canvas-borderLight'
                    : 'text-ink-muted hover:text-ink'
                }`}
              >
                {opt.label}
              </button>
            ))}
          </div>
        </div>

        {/* Numeric inputs row */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-2.5">
          <div>
            <label className="block text-[11px] font-mono text-ink-muted mb-1">
              Timeframe (Days)
            </label>
            <input
              type="number"
              min="1"
              step="1"
              placeholder="e.g. 30"
              value={timeframeDays}
              onChange={(e) => setTimeframeDays(e.target.value)}
              className={`w-full px-2.5 py-1.5 rounded bg-canvas-subtle border text-ink font-mono text-xs focus:ring-1 focus:ring-accent focus:outline-none transition-colors ${
                missingFields.includes('timeframe_days') ? 'border-red-500' : 'border-canvas-border'
              }`}
            />
          </div>

          <div>
            <label className="block text-[11px] font-mono text-ink-muted mb-1">
              Exit Target (₹)
            </label>
            <input
              type="number"
              min="0.1"
              step="any"
              placeholder="e.g. 950"
              value={exitTarget}
              onChange={(e) => setExitTarget(e.target.value)}
              className={`w-full px-2.5 py-1.5 rounded bg-canvas-subtle border text-ink font-mono text-xs focus:ring-1 focus:ring-accent focus:outline-none transition-colors ${
                missingFields.includes('exit_target') ? 'border-red-500' : 'border-canvas-border'
              }`}
            />
          </div>

          <div>
            <label className="block text-[11px] font-mono text-ink-muted mb-1">
              Max Loss Limit (%)
            </label>
            <input
              type="number"
              min="0.1"
              max="100"
              step="any"
              placeholder="e.g. 8"
              value={maxLossPct}
              onChange={(e) => setMaxLossPct(e.target.value)}
              className={`w-full px-2.5 py-1.5 rounded bg-canvas-subtle border text-ink font-mono text-xs focus:ring-1 focus:ring-accent focus:outline-none transition-colors ${
                missingFields.includes('max_loss_pct') ? 'border-red-500' : 'border-canvas-border'
              }`}
            />
          </div>
        </div>

        {/* Confidence selector 1 to 5 */}
        <div>
          <label className="block text-[11px] font-mono text-ink-muted mb-1.5">
            Conviction / Confidence (1–5)
          </label>
          <div className={`flex items-center gap-2 ${missingFields.includes('confidence') ? 'p-1 border border-red-500 rounded' : ''}`}>
            {[1, 2, 3, 4, 5].map((lvl) => (
              <button
                key={lvl}
                type="button"
                onClick={() => setConfidence(lvl)}
                className={`flex-1 py-1 rounded text-xs font-mono font-medium border transition-colors ${
                  confidence === lvl
                    ? 'bg-accent/15 border-accent text-accent'
                    : 'bg-canvas-subtle border-canvas-border text-ink-muted hover:text-ink hover:border-canvas-borderLight'
                }`}
              >
                {lvl}
              </button>
            ))}
          </div>
        </div>

        {/* Lock button */}
        <div className="pt-2">
          <button
            type="submit"
            disabled={!isFormValid || submitting}
            className={`w-full py-2 px-4 rounded text-xs font-mono uppercase tracking-wider font-medium flex items-center justify-center space-x-1.5 transition-all ${
              isFormValid && !submitting
                ? 'bg-accent text-black hover:bg-accent-hover cursor-pointer'
                : 'bg-canvas-hover border border-canvas-border text-ink-faint cursor-not-allowed'
            }`}
          >
            <Lock className="w-3.5 h-3.5 mr-1" />
            <span>{submitting ? 'Locking decision...' : 'Lock decision'}</span>
          </button>
        </div>
      </form>
    </div>
  );
}

export default DecisionGate;
