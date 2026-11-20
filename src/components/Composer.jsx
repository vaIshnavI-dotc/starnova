import React, { useState, useRef } from 'react';
import { ArrowUp, Image as ImageIcon, X } from 'lucide-react';

export function Composer({
  onSendMessage,
  disabled = false,
  quickReplies = [],
  stage,
  questionsAsked = 0,
  questionsMax = 6,
  placeholder = 'Reply to your butler...'
}) {
  const [text, setText] = useState('');
  const [imageFile, setImageFile] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);
  const fileInputRef = useRef(null);
  const textareaRef = useRef(null);

  const handleImageSelect = (e) => {
    const file = e.target.files?.[0];
    if (file) {
      setImageFile(file);
      const url = URL.createObjectURL(file);
      setImagePreview(url);
    }
  };

  const handleClearImage = () => {
    setImageFile(null);
    if (imagePreview) {
      URL.revokeObjectURL(imagePreview);
      setImagePreview(null);
    }
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const handleSend = () => {
    const trimmed = text.trim();
    if ((!trimmed && !imageFile) || disabled) return;

    onSendMessage({
      text: trimmed,
      image: imageFile
    });

    setText('');
    handleClearImage();

    // Reset textarea height
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleQuickReply = (qr) => {
    if (disabled) return;
    onSendMessage({
      text: qr.value,
      displayLabel: qr.label
    });
  };

  // Auto resize textarea
  const handleInput = (e) => {
    setText(e.target.value);
    e.target.style.height = 'auto';
    e.target.style.height = `${Math.min(e.target.scrollHeight, 140)}px`;
  };

  const canSend = (text.trim().length > 0 || imageFile !== null) && !disabled;

  return (
    <div className="w-full bg-canvas/90 backdrop-blur-md pt-2 pb-4 border-t border-canvas-border">
      <div className="max-w-[720px] mx-auto px-4 w-full">
        {/* Question Counter (shown subtly while stage is questioning) */}
        {stage === 'questioning' && (
          <div className="flex items-center justify-between mb-2 px-1">
            <span className="font-mono text-[11px] text-ink-muted">
              Question {questionsAsked} of {questionsMax}
            </span>
            <div className="flex items-center space-x-1">
              {Array.from({ length: questionsMax }).map((_, i) => (
                <div
                  key={i}
                  className={`w-1.5 h-1.5 rounded-full ${i < questionsAsked ? 'bg-accent' : 'bg-canvas-borderLight'}`}
                />
              ))}
            </div>
          </div>
        )}

        {/* Quick replies chips */}
        {quickReplies && quickReplies.length > 0 && (
          <div className="flex flex-wrap items-center gap-2 mb-2.5 px-1 animate-fade">
            {quickReplies.map((qr, idx) => (
              <button
                key={idx}
                type="button"
                onClick={() => handleQuickReply(qr)}
                disabled={disabled}
                className="px-3 py-1 rounded-full text-xs font-mono bg-canvas-card border border-canvas-border hover:border-canvas-borderLight hover:bg-canvas-hover text-ink transition-colors disabled:opacity-50"
              >
                {qr.label}
              </button>
            ))}
          </div>
        )}

        {/* Image thumbnail preview if attached */}
        {imagePreview && (
          <div className="relative inline-block mb-2 ml-1">
            <div className="w-16 h-16 rounded border border-canvas-border overflow-hidden bg-canvas-card">
              <img src={imagePreview} alt="Screenshot preview" className="w-full h-full object-cover" />
            </div>
            <button
              type="button"
              onClick={handleClearImage}
              className="absolute -top-1.5 -right-1.5 w-5 h-5 bg-canvas-card border border-canvas-border text-ink-muted hover:text-ink rounded-full flex items-center justify-center shadow focus:outline-none"
              title="Remove attachment"
            >
              <X className="w-3 h-3" />
            </button>
          </div>
        )}

        {/* Main Composer Box */}
        <div className="relative flex items-end bg-canvas-card border border-canvas-border hover:border-canvas-borderLight rounded-xl focus-within:border-accent/60 transition-colors p-1.5">
          {/* Screenshot upload button */}
          <button
            type="button"
            onClick={() => fileInputRef.current?.click()}
            disabled={disabled}
            className="p-2 text-ink-muted hover:text-ink disabled:opacity-40 transition-colors rounded-lg hover:bg-canvas-hover flex-shrink-0"
            title="Upload screenshot of tip"
          >
            <ImageIcon className="w-4 h-4" />
          </button>
          <input
            ref={fileInputRef}
            type="file"
            accept="image/*"
            onChange={handleImageSelect}
            className="hidden"
          />

          {/* Text input area */}
          <textarea
            ref={textareaRef}
            value={text}
            onChange={handleInput}
            onKeyDown={handleKeyDown}
            disabled={disabled}
            placeholder={placeholder}
            rows={1}
            className="w-full bg-transparent text-ink placeholder:text-ink-faint px-2 py-2 text-sm focus:outline-none resize-none max-h-36 leading-normal"
          />

          {/* Send button */}
          <button
            type="button"
            onClick={handleSend}
            disabled={!canSend}
            className={`p-2 rounded-lg flex-shrink-0 transition-colors ${
              canSend
                ? 'bg-accent text-black hover:bg-accent-hover cursor-pointer'
                : 'bg-canvas-hover text-ink-faint cursor-not-allowed'
            }`}
            title="Send message"
          >
            <ArrowUp className="w-4 h-4" />
          </button>
        </div>

        {/* Mandatory legal disclaimer copy */}
        <p className="text-center text-[11px] font-mono text-ink-faint mt-2 tracking-tight">
          Your financial thinking companion. Not an investment advisor.
        </p>
      </div>
    </div>
  );
}

export default Composer;
