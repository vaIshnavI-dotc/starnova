// Comprehensive mock fixtures matching API_CONTRACT.md exactly

export const MOCK_USER = {
  id: "u_demo",
  name: "Demo Investor",
  email: "demo@signalnoise.app"
};

export const MOCK_SOURCES = [
  {
    id: "s_2",
    name: "Neel",
    type: "friend",
    tips_total: 4,
    tips_worked: 1,
    raw_hit_rate: 0.25,
    shrunk_hit_rate: 0.31,
    ci_low: 0.08,
    ci_high: 0.65,
    evidence_level: "low",
    label: "Too early to tell"
  },
  {
    id: "s_1",
    name: "Kushal",
    type: "finfluencer",
    tips_total: 3,
    tips_worked: 2,
    raw_hit_rate: 0.67,
    shrunk_hit_rate: 0.52,
    ci_low: 0.21,
    ci_high: 0.83,
    evidence_level: "medium",
    label: "Limited sample"
  },
  {
    id: "s_3",
    name: "Anonymous",
    type: "anonymous",
    tips_total: 5,
    tips_worked: 1,
    raw_hit_rate: 0.20,
    shrunk_hit_rate: 0.22,
    ci_low: 0.05,
    ci_high: 0.54,
    evidence_level: "high",
    label: "Consistently negative"
  }
];

export const MOCK_ALERTS = [
  {
    id: "a_1",
    type: "outcome_confirmed",
    title: "30-Day Horizon Reached",
    body: "Tata Motors tip from Neel evaluated against Nifty 50 benchmark.",
    tip_id: "t_3",
    source_name: "Neel",
    results: {
      d7: { status: "worked", return_pct: 4.1, benchmark_pct: 1.2 },
      d30: { status: "worked", return_pct: 7.5, benchmark_pct: 3.2 },
      d90: { status: "pending", return_pct: null, benchmark_pct: null }
    },
    created_at: new Date(Date.now() - 2 * 3600 * 1000).toISOString(),
    read: false
  },
  {
    id: "a_2",
    type: "negative_outcome",
    title: "7-Day Stop Breached",
    body: "Suzlon tip from Telegram channel missed benchmark.",
    tip_id: "t_4",
    source_name: "Anonymous",
    results: {
      d7: { status: "missed", return_pct: -6.4, benchmark_pct: 0.8 },
      d30: { status: "pending", return_pct: null, benchmark_pct: null },
      d90: { status: "pending", return_pct: null, benchmark_pct: null }
    },
    created_at: new Date(Date.now() - 26 * 3600 * 1000).toISOString(),
    read: false
  },
  {
    id: "a_3",
    type: "new_update",
    title: "Pattern Warning Detected",
    body: "Repeated reliance on urgency tags ('next week', 'insider') preceding negative outcomes.",
    tip_id: "t_5",
    source_name: "System",
    results: {
      d7: { status: "pending", return_pct: null, benchmark_pct: null },
      d30: { status: "pending", return_pct: null, benchmark_pct: null },
      d90: { status: "pending", return_pct: null, benchmark_pct: null }
    },
    created_at: new Date(Date.now() - 48 * 3600 * 1000).toISOString(),
    read: true
  }
];

export const MOCK_INSIGHTS = [
  {
    id: "i_1",
    text: "You've bought after an 8%+ jump 4 times. 3 lost money.",
    evidence_count: 4
  },
  {
    id: "i_2",
    text: "Tips mentioning 'insider news' from messaging groups had an 18% hit rate over 90-day holding horizons.",
    evidence_count: 7
  }
];

export const MOCK_INVESTMENTS = [
  {
    id: "inv_1",
    ticker: "INFY",
    stock_name: "Infosys Ltd",
    quantity: 25,
    avg_price: 1480,
    purchase_date: "2026-10-15",
    current_price: 1540.5,
    current_value: 38512.5,
    linked_tip_id: null
  },
  {
    id: "inv_2",
    ticker: "RELIANCE",
    stock_name: "Reliance Industries",
    quantity: 15,
    avg_price: 2850,
    purchase_date: "2026-09-02",
    current_price: 2980.0,
    current_value: 44700.0,
    linked_tip_id: "t_1"
  }
];

export const MOCK_DECISIONS = [
  {
    id: "d_past_1",
    tip_id: "t_1",
    action: "bought",
    timeframe_days: 90,
    exit_target: 3100,
    max_loss_pct: 6,
    confidence: 4,
    thesis: "Energy transition capex and retail consolidation will compound FCF.",
    gaps_count: 1,
    locked_at: "2026-09-02T11:20:00Z",
    stock: { name: "Reliance Industries", ticker: "RELIANCE" },
    source_name: "Kushal"
  },
  {
    id: "d_past_2",
    tip_id: "t_4",
    action: "skipped",
    timeframe_days: 30,
    exit_target: 65,
    max_loss_pct: 10,
    confidence: 2,
    thesis: "Speculative momentum with no verifiable balance sheet backing.",
    gaps_count: 5,
    locked_at: "2026-11-12T16:45:00Z",
    stock: { name: "Suzlon Energy", ticker: "SUZLON" },
    source_name: "Anonymous"
  }
];
