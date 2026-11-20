import React from 'react';
import TextBlock from './TextBlock';
import ClaimCard from './ClaimCard';
import SourceChip from './SourceChip';
import ContextCard from './ContextCard';
import ThesisChain from './ThesisChain';
import DecisionGate from './DecisionGate';
import InsightCallout from './InsightCallout';
import InvestmentConfirm from './InvestmentConfirm';

export function BlockRenderer({ block, isNew = false, onDecisionLocked, onInvestmentConfirmed }) {
  if (!block || typeof block !== 'object') return null;

  switch (block.type) {
    case 'text':
      return <TextBlock block={block} isNew={isNew} />;
    case 'claim_card':
      return <ClaimCard block={block} />;
    case 'source_record':
      return <SourceChip block={block} />;
    case 'context_card':
      return <ContextCard block={block} />;
    case 'thesis_chain':
      return <ThesisChain block={block} />;
    case 'decision_gate':
      return <DecisionGate block={block} onDecisionLocked={onDecisionLocked} />;
    case 'insight':
      return <InsightCallout block={block} />;
    case 'investment_confirm':
      return <InvestmentConfirm block={block} onConfirmed={onInvestmentConfirmed} />;
    default:
      // Fallback to plain text for unknown types
      return (
        <div className="p-3 my-2 bg-canvas-card border border-canvas-border rounded text-xs text-ink-muted font-mono">
          {block.content || block.text || JSON.stringify(block)}
        </div>
      );
  }
}

export default BlockRenderer;
