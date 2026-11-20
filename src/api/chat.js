// Chat API: POST /chat/message (multipart/form-data), GET /conversations/{conversation_id}
import { USE_MOCK, mockDelay, request, getStoredConversationId, setStoredConversationId, ApiError } from './client';

const MOCK_STORAGE_KEY = 'sn_mock_conversations_v1';

function getMockStore() {
  try {
    const raw = localStorage.getItem(MOCK_STORAGE_KEY);
    return raw ? JSON.parse(raw) : {};
  } catch {
    return {};
  }
}

function saveMockStore(store) {
  try {
    localStorage.setItem(MOCK_STORAGE_KEY, JSON.stringify(store));
  } catch {
    // Ignore storage quota
  }
}

export function resetMockChatState() {
  try {
    localStorage.removeItem(MOCK_STORAGE_KEY);
  } catch {}
}

export async function getConversation(conversationId) {
  if (!conversationId) {
    throw new ApiError(404, { code: 'not_found', message: 'Conversation ID required' });
  }

  if (USE_MOCK) {
    await mockDelay(250);
    const store = getMockStore();
    const conv = store[conversationId];
    if (!conv) {
      // If none found in storage, return a clean empty conversation or 404
      throw new ApiError(404, { code: 'not_found', message: 'Conversation not found' });
    }
    return conv;
  }

  return request(`/conversations/${conversationId}`, { method: 'GET' });
}

export async function postChatMessage({ conversationId, text, image }) {
  if (!text && !image) {
    throw new ApiError(422, {
      code: 'validation_error',
      message: 'At least one of text or image is required',
      details: {}
    });
  }

  if (USE_MOCK) {
    await mockDelay(600); // realistic typing/processing delay
    const store = getMockStore();
    const convId = conversationId || getStoredConversationId() || `c_${Date.now()}`;
    setStoredConversationId(convId);

    let conv = store[convId];
    if (!conv) {
      conv = {
        conversation_id: convId,
        stage: 'intake',
        questions_asked: 0,
        questions_max: 6,
        messages: []
      };
    }

    // Determine user displayed content
    const displayText = text === '__dont_know__' ? "Don't know" : (text || (image ? 'Attached screenshot' : ''));
    let imageUrl = null;
    if (image instanceof File) {
      try {
        imageUrl = URL.createObjectURL(image);
      } catch {
        imageUrl = null;
      }
    }

    // Add user message
    const userMsg = {
      id: `m_${Date.now()}_u`,
      role: 'user',
      created_at: new Date().toISOString(),
      image_url: imageUrl,
      blocks: [
        {
          type: 'text',
          content: displayText
        }
      ]
    };
    conv.messages.push(userMsg);

    const lowerText = (text || '').toLowerCase();

    let responseStage = conv.stage;
    let questionsAsked = conv.questions_asked;
    let blocks = [];
    let quickReplies = [];

    // Scripted Path B: User announces purchase: "I bought 10 Tata shares at 200 yesterday"
    if (lowerText.includes('bought') && (lowerText.includes('tata') || lowerText.includes('share') || lowerText.includes('at'))) {
      blocks = [
        {
          type: 'investment_confirm',
          confirm_token: `tok_tata_${Date.now()}`,
          draft: {
            ticker: 'TATAMOTORS',
            stock_name: 'Tata Motors',
            quantity: 10,
            avg_price: 200,
            purchase_date: '2026-11-19'
          }
        }
      ];
      responseStage = 'chitchat';
      quickReplies = [];
    }
    // Scripted Path C: General query "what do you think of Tata?"
    else if (lowerText.includes('what do you think') || (lowerText.includes('should i') && !image)) {
      blocks = [
        {
          type: 'text',
          content: "I do not evaluate individual securities, provide recommendations, or forecast price movements. I exist to challenge your thesis and review external claims. If you have received a specific claim or tip regarding Tata Motors, forward or describe it here."
        }
      ];
      responseStage = 'chitchat';
      quickReplies = [];
    }
    // Scripted Path A: Core Butler Flow (Neel tip upload or description)
    else {
      // Step 1: Initial Tip Intake -> returns claim_card + source_record + context_card + thesis request
      if (conv.stage === 'intake' || conv.messages.filter(m => m.role === 'assistant').length === 0) {
        responseStage = 'awaiting_thesis';
        questionsAsked = 0;
        blocks = [
          {
            type: 'claim_card',
            tip_id: 't_9',
            sender: 'Neel',
            source_id: 's_2',
            stock: { name: 'Tata Motors', ticker: 'TATAMOTORS' },
            claim: 'Tata Motors will jump 15% next week on insider news',
            red_flags: ['urgency', 'unsupported_claim', 'guaranteed_returns']
          },
          {
            type: 'source_record',
            source_id: 's_2',
            source_name: 'Neel',
            tips_total: 4,
            tips_worked: 1,
            shrunk_hit_rate: 0.31,
            evidence_level: 'low',
            label: 'Too early to tell'
          },
          {
            type: 'context_card',
            ticker: 'TATAMOTORS',
            price_now: 812.4,
            change_7d_pct: 6.2,
            since_tip_pct: null,
            note: 'Already up 6.2% in the last 7 days.'
          },
          {
            type: 'text',
            content: "Neel claims Tata Motors will jump 15% next week on insider news. Before considering this, what is your own core thesis? Why do you believe this stock should move, independent of the forward?"
          }
        ];
        quickReplies = [];
      }
      // Step 2: User provides thesis text -> returns thesis_chain + Question 1 of 6
      else if (conv.stage === 'awaiting_thesis') {
        responseStage = 'questioning';
        questionsAsked = 1;
        blocks = [
          {
            type: 'thesis_chain',
            links: [
              {
                id: 'l_1',
                text: 'Commercial vehicle demand is cyclical and currently in an upswing',
                status: 'backed',
                evidence: {
                  summary: 'SIAM industry data confirms 12% YoY CV sales volume increase for the past quarter.',
                  source_url: 'https://www.siam.in/statistics'
                }
              },
              {
                id: 'l_2',
                text: 'EV segment margins reached operational breakeven',
                status: 'backed',
                evidence: {
                  summary: 'Q2 FY27 earnings release confirmed +3.2% EV segment EBITDA.',
                  source_url: 'https://www.tatamotors.com/investors'
                }
              },
              {
                id: 'l_3',
                text: "Next week's announced product event has not yet been priced in",
                status: 'unchecked',
                evidence: null
              },
              {
                id: 'l_4',
                text: 'The 15% weekly jump claim is backed by institutional order accumulation',
                status: 'no_evidence',
                evidence: null
              },
              {
                id: 'l_5',
                text: 'Battery pack component supply bottleneck has been cleared',
                status: 'no_evidence',
                evidence: null
              },
              {
                id: 'l_6',
                text: 'Commodity steel input costs will remain suppressed over the near term',
                status: 'unchecked',
                evidence: null
              }
            ],
            gaps_count: 3,
            total_links: 6,
            summary: '3 of 6 links have no evidence.'
          },
          {
            type: 'text',
            content: "Your structural points have backing, but short-term catalyst links remain unverified. What specific verifiable data points connect the alleged 'insider news' to an imminent 15% price adjustment within 7 trading days?"
          }
        ];
        quickReplies = [{ label: "Don't know", value: '__dont_know__' }];
      }
      // Step 3: Question 1 answered -> returns Question 2 of 6
      else if (conv.stage === 'questioning' && conv.questions_asked === 1) {
        responseStage = 'questioning';
        questionsAsked = 2;
        blocks = [
          {
            type: 'text',
            content: "Noted as an unverified dependency. Who is the underlying source behind Neel's forward, and why would material non-public information reach retail messaging groups before being reflected in institutional pricing?"
          }
        ];
        quickReplies = [{ label: "Don't know", value: '__dont_know__' }];
      }
      // Step 4: Question 2 answered -> returns insight + decision_gate block
      else if (conv.stage === 'questioning') {
        responseStage = 'gate';
        questionsAsked = 2;
        blocks = [
          {
            type: 'insight',
            text: "You've bought after an 8%+ jump 4 times. 3 lost money."
          },
          {
            type: 'decision_gate',
            decision_id: 'd_1',
            tip_id: 't_9',
            required_fields: ['action', 'timeframe_days', 'exit_target', 'max_loss_pct', 'confidence'],
            values: {
              action: null,
              timeframe_days: null,
              exit_target: null,
              max_loss_pct: null,
              confidence: null
            },
            locked: false,
            locked_at: null
          }
        ];
        quickReplies = [];
      }
      // Step 5: Post gate / locked chitchat
      else {
        responseStage = conv.stage;
        blocks = [
          {
            type: 'text',
            content: "Your rationale and risk limits are locked. We will monitor the outcome at 7, 30, and 90-day intervals against the benchmark index."
          }
        ];
        quickReplies = [];
      }
    }

    // Add assistant response to messages
    const assistantMsg = {
      id: `m_${Date.now()}_a`,
      role: 'assistant',
      created_at: new Date().toISOString(),
      image_url: null,
      blocks
    };
    conv.messages.push(assistantMsg);
    conv.stage = responseStage;
    conv.questions_asked = questionsAsked;

    store[convId] = conv;
    saveMockStore(store);

    return {
      conversation_id: convId,
      stage: responseStage,
      questions_asked: questionsAsked,
      questions_max: 6,
      blocks,
      quick_replies: quickReplies
    };
  }

  // Real backend: POST /chat/message with multipart/form-data
  const formData = new FormData();
  if (conversationId) formData.append('conversation_id', conversationId);
  if (text) formData.append('text', text);
  if (image) formData.append('image', image);

  const res = await request('/chat/message', {
    method: 'POST',
    body: formData
  });

  if (res?.conversation_id) {
    setStoredConversationId(res.conversation_id);
  }

  return res;
}
