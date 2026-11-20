import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { AlertCircle, ArrowRight } from 'lucide-react';

export function SignupPage() {
  const { signup } = useAuth();
  const navigate = useNavigate();

  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!name || !email || !password || loading) return;

    setLoading(true);
    setError(null);

    try {
      await signup(name, email, password);
      navigate('/');
    } catch (err) {
      setError(err.message || 'Registration failed. Please try again.');
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
          Create Investor Profile
        </p>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
        <div className="bg-canvas-card py-8 px-6 border border-canvas-border rounded-xl shadow-xl sm:px-10">
          <form className="space-y-4" onSubmit={handleSubmit}>
            {error && (
              <div className="p-3 rounded bg-red-950/30 border border-red-800/40 text-red-300 text-xs font-mono flex items-center space-x-2">
                <AlertCircle className="w-4 h-4 flex-shrink-0" />
                <span>{error}</span>
              </div>
            )}

            <div>
              <label className="block text-xs font-mono uppercase text-ink-muted mb-1.5">
                Full Name
              </label>
              <input
                type="text"
                required
                value={name}
                onChange={(e) => setName(e.target.value)}
                className="w-full px-3 py-2 rounded bg-canvas-subtle border border-canvas-border text-sm text-ink font-mono focus:ring-1 focus:ring-accent focus:outline-none transition-colors"
                placeholder="Rohan Sharma"
              />
            </div>

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
                placeholder="rohan@example.com"
              />
            </div>

            <div>
              <label className="block text-xs font-mono uppercase text-ink-muted mb-1.5">
                Password
              </label>
              <input
                type="password"
                required
                minLength={6}
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
                <span>{loading ? 'Creating Profile...' : 'Sign Up'}</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </button>
            </div>
          </form>

          <div className="mt-6 pt-4 border-t border-canvas-border text-center">
            <Link
              to="/login"
              className="text-xs font-mono text-ink-muted hover:text-ink transition-colors"
            >
              Already have an account? Sign in →
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}

export default SignupPage;
