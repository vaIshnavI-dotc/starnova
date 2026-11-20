import React, { useState, useEffect } from 'react';

export function TextBlock({ block, isNew = false }) {
  const content = block?.content || '';
  const [displayedText, setDisplayedText] = useState(isNew ? '' : content);

  useEffect(() => {
    if (!isNew) {
      setDisplayedText(content);
      return;
    }

    let currentIndex = 0;
    const speed = Math.max(8, Math.min(24, Math.floor(600 / (content.length || 1))));
    const timer = setInterval(() => {
      currentIndex += 3;
      if (currentIndex >= content.length) {
        setDisplayedText(content);
        clearInterval(timer);
      } else {
        setDisplayedText(content.slice(0, currentIndex));
      }
    }, speed);

    return () => clearInterval(timer);
  }, [content, isNew]);

  return (
    <div className="text-sm leading-relaxed text-ink space-y-2 font-normal animate-fade">
      {displayedText.split('\n\n').map((paragraph, idx) => (
        <p key={idx} className="whitespace-pre-wrap">
          {paragraph}
        </p>
      ))}
    </div>
  );
}

export default TextBlock;
