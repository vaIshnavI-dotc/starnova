import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { AlertCircle, ArrowRight } from 'lucide-react';

export function LoginPage() {
  const { login } = useAuth();
  const navigate = useNavigate();

  const [email, setEmail] = useState('demo@signalnoise.app');
  const [password, setPassword] = useState('demo1234');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!email || !password || loading) return;

    setLoading(true);
    setError(null);

    try {
      await login(email, password);
      navigate('/');
    } catch (err) {
      setError(err.message || 'Authentication failed. Please verify credentials.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-canvas text-ink flex flex-col justify-center py-12 px-4 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-md text-center">
        <div className="font-mono text-base tracking-widest text-ink font-medium flex items-center justify-center space-x-2 mb-2">
          <span className="text-accent">◈</span>
          <span>SIGNAL / NOISE</span>
        </div>
        <p className="font-mono text-xs text-ink-muted">
          Retail Financial Thinking Companion
        </p>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
        <div className="bg-canvas-card py-8 px-6 border border-canvas-border rounded-xl shadow-xl sm:px-10">
          <form className="space-y-5" onSubmit={handleSubmit}>
            {error && (
              <div className="p-3 rounded bg-red-950/30 border border-red-800/40 text-red-300 text-xs font-mono flex items-center space-x-2">
                <AlertCircle className="w-4 h-4 flex-shrink-0" />
                <span>{error}</span>
              </div>
            )}

            <div>
              <label className="block text-xs font-mono uppercase text-ink-muted mb-1.5">
                Email Address
              </label>
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full px-3 py-2 rounded bg-canvas-subtle border border-canvas-border text-sm text-ink font-mono focus:ring-1 focus:ring-accent focus:outline-none transition-colors"
                placeholder="name@example.com"
              />
            </div>

            <div>
              <div className="flex items-center justify-between mb-1.5">
                <label className="block text-xs font-mono uppercase text-ink-muted">
                  Password
                </label>
              </div>
              <input
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full px-3 py-2 rounded bg-canvas-subtle border border-canvas-border text-sm text-ink font-mono focus:ring-1 focus:ring-accent focus:outline-none transition-colors"
                placeholder="••••••••"
              />
            </div>

            <div className="pt-2">
              <button
                type="submit"
                disabled={loading}
                className="w-full py-2.5 px-4 rounded text-xs font-mono uppercase tracking-wider font-medium bg-accent text-black hover:bg-accent-hover transition-colors flex items-center justify-center space-x-1.5 disabled:opacity-50 cursor-pointer"
              >
                <span>{loading ? 'Authenticating...' : 'Sign In'}</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </button>
            </div>
          </form>

          {/* Quick Demo Credentials hint */}
          <div className="mt-6 pt-4 border-t border-canvas-border text-center">
            <p className="text-[11px] font-mono text-ink-faint">
              Demo account seeded: <span className="text-ink-muted">demo@signalnoise.app / demo1234</span>
            </p>
          </div>

          <div className="mt-4 text-center">
            <Link
              to="/signup"
              className="text-xs font-mono text-ink-muted hover:text-ink transition-colors"
            >
              No account yet? Register here →
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}

export default LoginPage;
