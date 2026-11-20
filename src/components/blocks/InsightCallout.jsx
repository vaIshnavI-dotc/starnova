import React from 'react';
import { Compass } from 'lucide-react';

export function InsightCallout({ block }) {
  const { text } = block || {};
  if (!text) return null;

  return (
    <div className="w-full my-2.5 p-3.5 bg-canvas-card border-l-2 border-l-accent border border-canvas-border rounded-r-lg text-xs animate-fade">
      <div className="flex items-start space-x-2.5">
        <Compass className="w-4 h-4 text-accent flex-shrink-0 mt-0.5" />
        <div>
          <span className="font-mono text-[10px] uppercase tracking-wider text-accent block mb-1">
            Historical Pattern Insight
          </span>
          <p className="text-ink text-xs leading-relaxed font-normal">
            {text}
          </p>
        </div>
      </div>
    </div>
  );
}

export default InsightCallout;
