import React, { useState } from 'react';
import { Check, Edit2, X, CheckCircle2, AlertCircle } from 'lucide-react';
import { confirmInvestment } from '../../api';
import { formatINR, formatDate } from '../../utils/formatters';

export function InvestmentConfirm({ block, onConfirmed }) {
  const { confirm_token, draft = {} } = block || {};

  const [ticker, setTicker] = useState(draft.ticker || '');
  const [stockName, setStockName] = useState(draft.stock_name || '');
  const [quantity, setQuantity] = useState(draft.quantity || '');
  const [avgPrice, setAvgPrice] = useState(draft.avg_price || '');
  const [purchaseDate, setPurchaseDate] = useState(draft.purchase_date || '');

  const [isEditing, setIsEditing] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [confirmedData, setConfirmedData] = useState(null);
  const [isDismissed, setIsDismissed] = useState(false);
  const [error, setError] = useState(null);

  if (isDismissed) {
    return (
      <div className="w-full my-2 p-2.5 rounded bg-canvas-card border border-canvas-border text-[11px] font-mono text-ink-faint flex items-center justify-between">
        <span>Draft confirmation dismissed.</span>
      </div>
    );
  }

  if (confirmedData) {
    return (
      <div className="w-full my-2.5 p-3.5 bg-canvas-card border border-accent/40 rounded-lg text-xs animate-fade">
        <div className="flex items-center space-x-2 text-accent mb-2">
          <CheckCircle2 className="w-4 h-4" />
          <span className="font-mono uppercase tracking-wider text-xs font-medium">
            Recorded in your investments
          </span>
        </div>
        <div className="text-ink text-xs font-mono">
          {confirmedData.quantity} shares of {confirmedData.stock_name || confirmedData.ticker} @ {formatINR(confirmedData.avg_price)}
        </div>
        <div className="text-[11px] text-ink-muted mt-1 font-mono">
          Recorded for {formatDate(confirmedData.purchase_date)}
        </div>
      </div>
    );
  }

  const handleConfirm = async () => {
    setSubmitting(true);
    setError(null);
    try {
      const res = await confirmInvestment({
        confirm_token,
        ticker,
        quantity: Number(quantity),
        avg_price: Number(avgPrice),
        purchase_date: purchaseDate
      });

      if (res?.investment) {
        setConfirmedData(res.investment);
        if (onConfirmed) onConfirmed(res.investment);
      }
    } catch (err) {
      setError(err.message || 'Failed to confirm record.');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="w-full bg-canvas-card border border-canvas-border rounded-lg p-4 my-2.5 text-xs animate-fade">
      <div className="flex items-center justify-between pb-2 mb-3 border-b border-canvas-border">
        <span className="font-mono text-xs uppercase tracking-wider text-ink font-medium">
          Confirm Asset Record
        </span>
        <span className="font-mono text-[10px] text-ink-muted bg-canvas-hover px-1.5 py-0.5 rounded border border-canvas-border">
          Verification
        </span>
      </div>

      {error && (
        <div className="mb-2.5 p-2 rounded bg-red-950/30 border border-red-800/40 text-red-300 text-xs flex items-center space-x-1.5">
          <AlertCircle className="w-3.5 h-3.5 flex-shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {isEditing ? (
        <div className="space-y-2.5 mb-3">
          <div className="grid grid-cols-2 gap-2">
            <div>
              <label className="block text-[10px] font-mono text-ink-muted mb-1">Ticker</label>
              <input
                type="text"
                value={ticker}
                onChange={(e) => setTicker(e.target.value.toUpperCase())}
                className="w-full px-2 py-1 rounded bg-canvas-subtle border border-canvas-border text-xs text-ink font-mono focus:ring-1 focus:ring-accent focus:outline-none"
              />
            </div>
            <div>
              <label className="block text-[10px] font-mono text-ink-muted mb-1">Quantity</label>
              <input
                type="number"
                min="1"
                value={quantity}
                onChange={(e) => setQuantity(e.target.value)}
                className="w-full px-2 py-1 rounded bg-canvas-subtle border border-canvas-border text-xs text-ink font-mono focus:ring-1 focus:ring-accent focus:outline-none"
              />
            </div>
          </div>
          <div className="grid grid-cols-2 gap-2">
            <div>
              <label className="block text-[10px] font-mono text-ink-muted mb-1">Avg Price (₹)</label>
              <input
                type="number"
                step="any"
                value={avgPrice}
                onChange={(e) => setAvgPrice(e.target.value)}
                className="w-full px-2 py-1 rounded bg-canvas-subtle border border-canvas-border text-xs text-ink font-mono focus:ring-1 focus:ring-accent focus:outline-none"
              />
            </div>
            <div>
              <label className="block text-[10px] font-mono text-ink-muted mb-1">Purchase Date</label>
              <input
                type="date"
                value={purchaseDate}
                onChange={(e) => setPurchaseDate(e.target.value)}
                className="w-full px-2 py-1 rounded bg-canvas-subtle border border-canvas-border text-xs text-ink font-mono focus:ring-1 focus:ring-accent focus:outline-none"
              />
            </div>
          </div>
        </div>
      ) : (
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 mb-3">
          <div className="p-2 rounded bg-canvas-hover border border-canvas-border">
            <span className="block text-[10px] font-mono text-ink-muted">Asset</span>
            <span className="font-mono text-xs text-ink font-medium mt-0.5 block">{stockName || ticker}</span>
          </div>
          <div className="p-2 rounded bg-canvas-hover border border-canvas-border">
            <span className="block text-[10px] font-mono text-ink-muted">Quantity</span>
            <span className="font-mono text-xs text-ink font-medium mt-0.5 block">{quantity}</span>
          </div>
          <div className="p-2 rounded bg-canvas-hover border border-canvas-border">
            <span className="block text-[10px] font-mono text-ink-muted">Avg Price</span>
            <span className="font-mono text-xs text-ink font-medium mt-0.5 block">{formatINR(avgPrice)}</span>
          </div>
          <div className="p-2 rounded bg-canvas-hover border border-canvas-border">
            <span className="block text-[10px] font-mono text-ink-muted">Date</span>
            <span className="font-mono text-xs text-ink font-medium mt-0.5 block">{formatDate(purchaseDate)}</span>
          </div>
        </div>
      )}

      {/* Action buttons */}
      <div className="flex items-center justify-between pt-2 border-t border-canvas-border">
        <button
          type="button"
          onClick={() => setIsDismissed(true)}
          className="text-xs text-ink-muted hover:text-ink font-mono flex items-center transition-colors"
        >
          <X className="w-3.5 h-3.5 mr-1" />
          Cancel
        </button>

        <div className="flex items-center space-x-2">
          <button
            type="button"
            onClick={() => setIsEditing(!isEditing)}
            className="px-2.5 py-1 rounded border border-canvas-border text-xs text-ink hover:bg-canvas-hover font-mono flex items-center transition-colors"
          >
            <Edit2 className="w-3 h-3 mr-1" />
            {isEditing ? 'Done Editing' : 'Edit'}
          </button>

          <button
            type="button"
            onClick={handleConfirm}
            disabled={submitting}
            className="px-3 py-1 rounded bg-accent text-black font-mono text-xs font-medium hover:bg-accent-hover flex items-center transition-colors disabled:opacity-50"
          >
            <Check className="w-3.5 h-3.5 mr-1" />
            {submitting ? 'Confirming...' : 'Confirm'}
          </button>
        </div>
      </div>
    </div>
  );
}

export default InvestmentConfirm;
