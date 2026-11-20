import React from 'react';
import BlockRenderer from './blocks/BlockRenderer';

export function MessageBubble({ message, isLatest = false, onDecisionLocked, onInvestmentConfirmed }) {
  const { role, blocks = [], image_url, created_at } = message || {};
  const isUser = role === 'user';

  if (isUser) {
    return (
      <div className="flex justify-end my-3.5 animate-fade">
        <div className="max-w-[85%] sm:max-w-[75%] bg-canvas-card border border-canvas-border hover:border-canvas-borderLight rounded-2xl rounded-tr-xs px-4 py-2.5 shadow-sm transition-colors">
          {image_url && (
            <div className="mb-2 overflow-hidden rounded border border-canvas-border">
              <img
                src={image_url}
                alt="Uploaded screenshot"
                className="max-h-48 w-auto object-cover rounded"
              />
            </div>
          )}

          <div className="text-sm text-ink leading-relaxed font-normal">
            {blocks.map((block, idx) => (
              <span key={idx} className="whitespace-pre-wrap">
                {block.content || block.text || ''}
              </span>
            ))}
          </div>
        </div>
      </div>
    );
  }

  // Assistant message: left-aligned without bubbles
  return (
    <div className="w-full my-5 animate-fade">
      <div className="space-y-3">
        {blocks.map((block, idx) => (
          <BlockRenderer
            key={idx}
            block={block}
            isNew={isLatest}
            onDecisionLocked={onDecisionLocked}
            onInvestmentConfirmed={onInvestmentConfirmed}
          />
        ))}
      </div>
    </div>
  );
}

export default MessageBubble;
