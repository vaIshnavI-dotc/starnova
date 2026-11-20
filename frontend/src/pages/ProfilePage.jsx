import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { ArrowLeft, User, Shield, AlertCircle } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { getSources, USE_MOCK } from '../api';

export function ProfilePage() {
  const { user } = useAuth();
  const [sources, setSources] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    let isMounted = true;
    async function loadSourcesData() {
      setLoading(true);
      setError(null);
      try {
        const res = await getSources();
        if (isMounted && res?.sources) {
          setSources(res.sources);
        }
      } catch (err) {
        if (isMounted) {
          setError(err.message || 'Unable to load sources record.');
        }
      } finally {
        if (isMounted) {
          setLoading(false);
        }
      }
    }

    loadSourcesData();
    return () => { isMounted = false; };
  }, []);

  const evidenceLevelBadge = (level) => {
    const map = {
      none: 'text-ink-faint border-canvas-border',
      low: 'text-amber-400 bg-amber-950/20 border-amber-800/40',
      medium: 'text-ink-muted bg-canvas-hover border-canvas-borderLight',
      high: 'text-accent bg-accent/10 border-accent/30'
    };
    return map[level] || map.none;
  };

  return (
    <div className="min-h-screen bg-canvas text-ink py-8 px-4 sm:px-6">
      <div className="max-w-[720px] mx-auto">
        {/* Navigation Header */}
        <div className="mb-6">
          <Link
            to="/"
            className="inline-flex items-center text-xs font-mono text-ink-muted hover:text-ink transition-colors"
          >
            <ArrowLeft className="w-3.5 h-3.5 mr-1.5" />
            Back to thinking companion
          </Link>
        </div>

        {/* Profile Card */}
        <div className="bg-canvas-card border border-canvas-border rounded-xl p-5 mb-6">
          <div className="flex items-center space-x-4 pb-4 border-b border-canvas-border">
            <div className="w-12 h-12 rounded-full bg-canvas-hover border border-canvas-border flex items-center justify-center text-accent font-mono text-base">
              <User className="w-6 h-6" />
            </div>
            <div>
              <h1 className="text-base font-medium text-ink">
                {user?.name || 'Investor Profile'}
              </h1>
              <p className="font-mono text-xs text-ink-muted">
                {user?.email || 'demo@signalnoise.app'}
              </p>
            </div>
          </div>

          <div className="pt-3 flex items-center justify-between text-xs font-mono text-ink-muted">
            <span>Role: Retail Market Participant</span>
            <span className="flex items-center text-accent">
              <Shield className="w-3.5 h-3.5 mr-1" />
              Contract-Verified Client
            </span>
          </div>
        </div>

        {/* Sources Section */}
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="font-mono text-xs uppercase tracking-wider text-ink font-medium">
              Tracked Tip Sources
            </h2>
            {USE_MOCK && (
              <span className="font-mono text-[10px] text-amber-400 bg-amber-950/30 px-2 py-0.5 rounded border border-amber-800/40">
                Demo data
              </span>
            )}
          </div>

          {loading ? (
            <div className="p-8 text-center font-mono text-xs text-ink-muted bg-canvas-card border border-canvas-border rounded-xl">
              Retrieving sources track record...
            </div>
          ) : error ? (
            <div className="p-4 rounded-xl bg-red-950/30 border border-red-800/40 text-red-300 text-xs font-mono flex items-center space-x-2">
              <AlertCircle className="w-4 h-4 flex-shrink-0" />
              <span>{error}</span>
            </div>
          ) : sources.length === 0 ? (
            <div className="p-8 text-center font-mono text-xs text-ink-faint bg-canvas-card border border-canvas-border rounded-xl">
              No sources logged yet.
            </div>
          ) : (
            <div className="space-y-3">
              {sources.map((src) => {
                const ciAvailable = src.ci_low !== null && src.ci_low !== undefined && src.ci_high !== null && src.ci_high !== undefined;

                return (
                  <div
                    key={src.id}
                    className="p-4 rounded-xl bg-canvas-card border border-canvas-border hover:border-canvas-borderLight transition-colors"
                  >
                    <div className="flex items-start justify-between gap-2 pb-2 mb-2 border-b border-canvas-border">
                      <div className="flex items-center space-x-2">
                        <span className="font-medium text-sm text-ink">{src.name}</span>
                        <span className="text-[10px] font-mono uppercase px-1.5 py-0.5 rounded bg-canvas-hover border border-canvas-border text-ink-muted">
                          {src.type}
                        </span>
                      </div>

                      <div className="flex items-center space-x-1.5">
                        {src.label && (
                          <span className="font-mono text-[10px] px-2 py-0.5 rounded bg-canvas-hover border border-canvas-border text-ink">
                            {src.label}
                          </span>
                        )}
                        {src.evidence_level && (
                          <span className={`font-mono text-[10px] uppercase px-1.5 py-0.5 rounded border ${evidenceLevelBadge(src.evidence_level)}`}>
                            ev: {src.evidence_level}
                          </span>
                        )}
                      </div>
                    </div>

                    <div className="grid grid-cols-2 sm:grid-cols-3 gap-2 text-xs font-mono mt-2">
                      <div className="p-2 rounded bg-canvas-hover border border-canvas-border">
                        <div className="text-[10px] text-ink-muted uppercase">Record</div>
                        <div className="text-ink font-medium mt-0.5">
                          {src.tips_worked} of {src.tips_total} worked
                        </div>
                      </div>

                      <div className="p-2 rounded bg-canvas-hover border border-canvas-border">
                        <div className="text-[10px] text-ink-muted uppercase">Shrunk Rate</div>
                        <div className="text-ink font-medium mt-0.5">
                          {Math.round(src.shrunk_hit_rate * 100)}%
                        </div>
                      </div>

                      <div className="p-2 rounded bg-canvas-hover border border-canvas-border col-span-2 sm:col-span-1">
                        <div className="text-[10px] text-ink-muted uppercase">Confidence Interval</div>
                        <div className="text-ink font-medium mt-0.5">
                          {ciAvailable ? `${Math.round(src.ci_low * 100)}% – ${Math.round(src.ci_high * 100)}%` : '—'}
                        </div>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default ProfilePage;
