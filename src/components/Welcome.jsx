import React, { useState, useRef } from 'react';
import { ArrowUp, Image as ImageIcon, X } from 'lucide-react';

export function Welcome({ onSendMessage, disabled = false }) {
  const [text, setText] = useState('');
  const [imageFile, setImageFile] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);
  const fileInputRef = useRef(null);

  // Time-based greeting
  const getGreeting = () => {
    const hour = new Date().getHours();
    if (hour >= 5 && hour < 12) return 'Good morning.';
    if (hour >= 12 && hour < 17) return 'Good afternoon.';
    if (hour >= 17 && hour < 22) return 'Good evening.';
    return 'Good evening.';
  };

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
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const sampleSuggestions = [
    { label: "Neel's Tip", text: "Neel forwarded a tip: Tata Motors will jump 15% next week on insider news" },
    { label: "Record Asset", text: "I bought 10 Tata shares at 200 yesterday" },
    { label: "Stock Query", text: "what do you think of Tata?" }
  ];

  const canSend = (text.trim().length > 0 || imageFile !== null) && !disabled;

  return (
    <div className="flex-1 flex flex-col items-center justify-center px-4 py-8 max-w-[640px] mx-auto w-full text-center animate-fade">
      <div className="w-10 h-10 rounded-full border border-canvas-border flex items-center justify-center text-accent mb-6 bg-canvas-card">
        <span className="font-mono text-base">◈</span>
      </div>

      <div className="space-y-1.5 mb-8">
        <div className="font-mono text-xs uppercase tracking-wider text-ink-muted">
          {getGreeting()}
        </div>
        <h1 className="text-2xl font-medium tracking-tight text-ink">
          Let's think before we act.
        </h1>
        <p className="text-lg text-ink font-normal">
          What have you heard today?
        </p>
        <p className="text-xs text-ink-muted max-w-md mx-auto pt-1 leading-relaxed">
          Share a stock tip, forward a message, or question an investment idea.
        </p>
      </div>

      {/* Centred composer box */}
      <div className="w-full max-w-xl mx-auto mb-6 text-left">
        {imagePreview && (
          <div className="relative inline-block mb-2 ml-1">
            <div className="w-16 h-16 rounded border border-canvas-border overflow-hidden bg-canvas-card">
              <img src={imagePreview} alt="Screenshot preview" className="w-full h-full object-cover" />
            </div>
            <button
              type="button"
              onClick={handleClearImage}
              className="absolute -top-1.5 -right-1.5 w-5 h-5 bg-canvas-card border border-canvas-border text-ink-muted hover:text-ink rounded-full flex items-center justify-center shadow focus:outline-none"
            >
              <X className="w-3 h-3" />
            </button>
          </div>
        )}

        <div className="flex items-center bg-canvas-card border border-canvas-border hover:border-canvas-borderLight rounded-xl focus-within:border-accent/60 p-1.5 transition-colors shadow-sm">
          <button
            type="button"
            onClick={() => fileInputRef.current?.click()}
            disabled={disabled}
            className="p-2 text-ink-muted hover:text-ink disabled:opacity-40 transition-colors rounded-lg hover:bg-canvas-hover flex-shrink-0"
            title="Upload screenshot"
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

          <input
            type="text"
            value={text}
            onChange={(e) => setText(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={disabled}
            placeholder="Tell me what you've heard..."
            className="w-full bg-transparent text-ink placeholder:text-ink-faint px-3 py-2 text-sm focus:outline-none"
          />

          <button
            type="button"
            onClick={handleSend}
            disabled={!canSend}
            className={`p-2 rounded-lg flex-shrink-0 transition-colors ${
              canSend
                ? 'bg-accent text-black hover:bg-accent-hover cursor-pointer'
                : 'bg-canvas-hover text-ink-faint cursor-not-allowed'
            }`}
          >
            <ArrowUp className="w-4 h-4" />
          </button>
        </div>

        {/* Suggestion prompts */}
        <div className="mt-3 flex flex-wrap items-center justify-center gap-1.5">
          {sampleSuggestions.map((s, idx) => (
            <button
              key={idx}
              type="button"
              onClick={() => onSendMessage({ text: s.text })}
              className="px-2.5 py-1 rounded-full text-[11px] font-mono bg-canvas-card border border-canvas-border hover:border-canvas-borderLight hover:bg-canvas-hover text-ink-muted hover:text-ink transition-colors"
            >
              {s.label}
            </button>
          ))}
        </div>
      </div>

      <p className="text-[11px] font-mono text-ink-faint tracking-tight">
        Your financial thinking companion. Not an investment advisor.
      </p>
    </div>
  );
}

export default Welcome;
