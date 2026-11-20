import React, { useState, useEffect, useRef } from 'react';
import MessageBubble from './MessageBubble';
import Composer from './Composer';
import Welcome from './Welcome';
import {
  getStoredConversationId,
  setStoredConversationId,
  getConversation,
  postChatMessage
} from '../api';

export function ChatWindow() {
  const [messages, setMessages] = useState([]);
  const [stage, setStage] = useState('intake');
  const [questionsAsked, setQuestionsAsked] = useState(0);
  const [questionsMax, setQuestionsMax] = useState(6);
  const [quickReplies, setQuickReplies] = useState([]);
  const [loading, setLoading] = useState(false);
  const [initialLoading, setInitialLoading] = useState(true);
  const [error, setError] = useState(null);

  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading]);

  // Load existing conversation on mount if present
  useEffect(() => {
    let isMounted = true;
    async function loadSavedConversation() {
      const storedId = getStoredConversationId();
      if (!storedId) {
        if (isMounted) setInitialLoading(false);
        return;
      }

      try {
        const res = await getConversation(storedId);
        if (isMounted && res) {
          setMessages(res.messages || []);
          setStage(res.stage || 'intake');
          setQuestionsAsked(res.questions_asked || 0);
          setQuestionsMax(res.questions_max || 6);
        }
      } catch (err) {
        console.warn('Could not reload stored conversation', err);
        // Clean stale ID
        setStoredConversationId(null);
      } finally {
        if (isMounted) setInitialLoading(false);
      }
    }

    loadSavedConversation();
    return () => { isMounted = false; };
  }, []);

  const handleSendMessage = async ({ text, image, displayLabel }) => {
    if (loading) return;

    setError(null);
    setLoading(true);

    const storedId = getStoredConversationId();

    // Optimistically add user message to list
    const tempUserMsg = {
      id: `m_temp_${Date.now()}`,
      role: 'user',
      created_at: new Date().toISOString(),
      image_url: image ? URL.createObjectURL(image) : null,
      blocks: [
        {
          type: 'text',
          content: displayLabel || (text === '__dont_know__' ? "Don't know" : text) || (image ? 'Attached screenshot' : '')
        }
      ]
    };

    setMessages((prev) => [...prev, tempUserMsg]);

    try {
      const res = await postChatMessage({
        conversationId: storedId,
        text,
        image
      });

      if (res?.conversation_id) {
        setStoredConversationId(res.conversation_id);
      }
      if (res?.stage) setStage(res.stage);
      if (typeof res?.questions_asked === 'number') setQuestionsAsked(res.questions_asked);
      if (typeof res?.questions_max === 'number') setQuestionsMax(res.questions_max);
      setQuickReplies(res?.quick_replies || []);

      // Assistant response message
      if (res?.blocks && res.blocks.length > 0) {
        const assistantMsg = {
          id: `m_a_${Date.now()}`,
          role: 'assistant',
          created_at: new Date().toISOString(),
          image_url: null,
          blocks: res.blocks
        };
        setMessages((prev) => [...prev, assistantMsg]);
      }
    } catch (err) {
      setError(err.message || 'Failed to deliver message. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleDecisionLocked = (lockedDecision) => {
    // Optionally update stage to locked
    setStage('locked');
  };

  const handleInvestmentConfirmed = (confirmedInvestment) => {
    // Investment confirmed
  };

  if (initialLoading) {
    return (
      <div className="flex-1 flex items-center justify-center font-mono text-xs text-ink-muted">
        Restoring conversation...
      </div>
    );
  }

  const hasMessages = messages.length > 0;

  return (
    <div className="flex-1 flex flex-col h-[calc(100vh-3.5rem)] overflow-hidden">
      {/* Scrollable Conversation Center */}
      <div className="flex-1 overflow-y-auto px-4 py-6">
        <div className="max-w-[720px] mx-auto w-full">
          {!hasMessages ? (
            <Welcome onSendMessage={handleSendMessage} disabled={loading} />
          ) : (
            <>
              {messages.map((msg, idx) => (
                <MessageBubble
                  key={msg.id || idx}
                  message={msg}
                  isLatest={idx === messages.length - 1}
                  onDecisionLocked={handleDecisionLocked}
                  onInvestmentConfirmed={handleInvestmentConfirmed}
                />
              ))}

              {/* In-flight typing/loading indicator */}
              {loading && (
                <div className="flex items-center space-x-2 py-4 text-xs font-mono text-ink-muted animate-fade">
                  <span className="text-accent">◈</span>
                  <span>Examining claims & testing logic...</span>
                  <div className="flex space-x-1">
                    <span className="w-1.5 h-1.5 bg-accent/70 rounded-full animate-bounce [animation-delay:-0.3s]" />
                    <span className="w-1.5 h-1.5 bg-accent/70 rounded-full animate-bounce [animation-delay:-0.15s]" />
                    <span className="w-1.5 h-1.5 bg-accent/70 rounded-full animate-bounce" />
                  </div>
                </div>
              )}

              {/* Error Callout */}
              {error && (
                <div className="my-3 p-3 rounded bg-red-950/30 border border-red-800/40 text-red-300 text-xs font-mono">
                  {error}
                </div>
              )}

              <div ref={messagesEndRef} />
            </>
          )}
        </div>
      </div>

      {/* Sticky Bottom Composer (shown when messages exist) */}
      {hasMessages && (
        <Composer
          onSendMessage={handleSendMessage}
          disabled={loading}
          quickReplies={quickReplies}
          stage={stage}
          questionsAsked={questionsAsked}
          questionsMax={questionsMax}
          placeholder="Reply to your butler..."
        />
      )}
    </div>
  );
}

export default ChatWindow;
