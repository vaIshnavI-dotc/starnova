import React, { useState, useRef, useEffect } from 'react';
import { Link as RouterLink, useNavigate } from 'react-router-dom';
import { Bell, User, LogOut, Briefcase } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { useAlerts } from '../context/AlertsContext';

export function TopBar() {
  const { user, logout } = useAuth();
  const { unreadCount, toggleDrawer } = useAlerts();
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const dropdownRef = useRef(null);
  const navigate = useNavigate();

  useEffect(() => {
    function handleClickOutside(e) {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target)) {
        setDropdownOpen(false);
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleLogout = () => {
    setDropdownOpen(false);
    logout();
    navigate('/login');
  };

  // Get user initials
  const initials = user?.name
    ? user.name.split(' ').map(n => n[0]).join('').slice(0, 2).toUpperCase()
    : 'SN';

  return (
    <header className="sticky top-0 z-30 w-full h-14 bg-canvas/95 backdrop-blur-md border-b border-canvas-border flex items-center justify-between px-4 sm:px-6">
      {/* Logo */}
      <RouterLink
        to="/"
        className="font-mono text-sm tracking-wider text-ink font-medium hover:text-accent transition-colors flex items-center space-x-2 focus:outline-none"
      >
        <span className="text-accent">◈</span>
        <span>SIGNAL / NOISE</span>
      </RouterLink>

      {/* Right Actions: Alerts Bell & Profile Dropdown */}
      <div className="flex items-center space-x-3">
        {/* Alerts Bell */}
        <button
          type="button"
          onClick={toggleDrawer}
          className="relative p-2 rounded-lg text-ink-muted hover:text-ink hover:bg-canvas-hover transition-colors focus:outline-none"
          title="Alerts and Horizon Outcomes"
          aria-label="Alerts"
        >
          <Bell className="w-4 h-4" />
          {unreadCount > 0 && (
            <span className="absolute top-2 right-2 w-2 h-2 rounded-full bg-accent ring-2 ring-canvas" />
          )}
        </button>

        {/* Profile Avatar Dropdown */}
        <div className="relative" ref={dropdownRef}>
          <button
            type="button"
            onClick={() => setDropdownOpen(prev => !prev)}
            className="flex items-center justify-center w-8 h-8 rounded-full bg-canvas-card border border-canvas-border hover:border-canvas-borderLight text-xs font-mono text-ink transition-colors focus:outline-none"
            aria-label="User profile menu"
          >
            {initials}
          </button>

          {dropdownOpen && (
            <div className="absolute right-0 mt-2 w-48 bg-canvas-card border border-canvas-border rounded-lg shadow-xl py-1 text-xs font-mono z-40 animate-fade">
              <div className="px-3 py-2 border-b border-canvas-border">
                <div className="text-ink font-medium truncate">{user?.name || 'Investor'}</div>
                <div className="text-[10px] text-ink-muted truncate">{user?.email || 'demo@signalnoise.app'}</div>
              </div>

              <RouterLink
                to="/profile"
                onClick={() => setDropdownOpen(false)}
                className="flex items-center px-3 py-2 text-ink-muted hover:text-ink hover:bg-canvas-hover transition-colors"
              >
                <User className="w-3.5 h-3.5 mr-2 text-ink-faint" />
                My profile
              </RouterLink>

              <RouterLink
                to="/investments"
                onClick={() => setDropdownOpen(false)}
                className="flex items-center px-3 py-2 text-ink-muted hover:text-ink hover:bg-canvas-hover transition-colors"
              >
                <Briefcase className="w-3.5 h-3.5 mr-2 text-ink-faint" />
                My investments
              </RouterLink>

              <div className="border-t border-canvas-border my-1" />

              <button
                type="button"
                onClick={handleLogout}
                className="w-full text-left flex items-center px-3 py-2 text-status-no_evidence hover:bg-canvas-hover transition-colors"
              >
                <LogOut className="w-3.5 h-3.5 mr-2" />
                Logout
              </button>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}

export default TopBar;
