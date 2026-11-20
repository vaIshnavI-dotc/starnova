import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { getAlerts, markAlertRead, markAllAlertsRead } from '../api';
import { useAuth } from './AuthContext';

const AlertsContext = createContext(null);

export function AlertsProvider({ children }) {
  const { isAuthenticated } = useAuth();
  const [alerts, setAlerts] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchAlerts = useCallback(async () => {
    if (!isAuthenticated) return;
    setLoading(true);
    setError(null);
    try {
      const res = await getAlerts();
      if (res) {
        setAlerts(res.alerts || []);
        setUnreadCount(res.unread_count ?? (res.alerts?.filter(a => !a.read).length || 0));
      }
    } catch (err) {
      setError(err.message || 'Failed to load alerts');
    } finally {
      setLoading(false);
    }
  }, [isAuthenticated]);

  useEffect(() => {
    if (isAuthenticated) {
      fetchAlerts();
    } else {
      setAlerts([]);
      setUnreadCount(0);
      setDrawerOpen(false);
    }
  }, [isAuthenticated, fetchAlerts]);

  const markSingleRead = useCallback(async (alertId) => {
    try {
      // Optimistic update
      setAlerts(prev => prev.map(a => a.id === alertId ? { ...a, read: true } : a));
      setUnreadCount(prev => Math.max(0, prev - 1));
      const res = await markAlertRead(alertId);
      if (res && typeof res.unread_count === 'number') {
        setUnreadCount(res.unread_count);
      }
    } catch (err) {
      console.error('Failed to mark alert as read', err);
      // Refresh to restore accurate state
      fetchAlerts();
    }
  }, [fetchAlerts]);

  const markAllRead = useCallback(async () => {
    try {
      // Optimistic update
      setAlerts(prev => prev.map(a => ({ ...a, read: true })));
      setUnreadCount(0);
      await markAllAlertsRead();
    } catch (err) {
      console.error('Failed to mark all alerts as read', err);
      fetchAlerts();
    }
  }, [fetchAlerts]);

  const value = {
    alerts,
    unreadCount,
    drawerOpen,
    setDrawerOpen,
    toggleDrawer: () => setDrawerOpen(prev => !prev),
    loading,
    error,
    refreshAlerts: fetchAlerts,
    markSingleRead,
    markAllRead
  };

  return (
    <AlertsContext.Provider value={value}>
      {children}
    </AlertsContext.Provider>
  );
}

export function useAlerts() {
  const context = useContext(AlertsContext);
  if (!context) {
    throw new Error('useAlerts must be used within an AlertsProvider');
  }
  return context;
}
