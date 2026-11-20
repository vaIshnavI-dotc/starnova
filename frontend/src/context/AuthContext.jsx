import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { getToken, getMe, login as apiLogin, signup as apiSignup, logout as apiLogout } from '../api';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(() => getToken());
  const [loading, setLoading] = useState(true);

  // Initialize auth state
  useEffect(() => {
    let isMounted = true;
    async function loadUser() {
      const storedToken = getToken();
      if (!storedToken) {
        if (isMounted) {
          setUser(null);
          setLoading(false);
        }
        return;
      }

      try {
        const res = await getMe();
        if (isMounted && res?.user) {
          setUser(res.user);
        }
      } catch (err) {
        if (isMounted) {
          apiLogout();
          setUser(null);
          setToken(null);
        }
      } finally {
        if (isMounted) {
          setLoading(false);
        }
      }
    }

    loadUser();
    return () => { isMounted = false; };
  }, []);

  const login = useCallback(async (email, password) => {
    const res = await apiLogin({ email, password });
    if (res?.token && res?.user) {
      setToken(res.token);
      setUser(res.user);
    }
    return res;
  }, []);

  const signup = useCallback(async (name, email, password) => {
    const res = await apiSignup({ name, email, password });
    if (res?.token && res?.user) {
      setToken(res.token);
      setUser(res.user);
    }
    return res;
  }, []);

  const logout = useCallback(() => {
    apiLogout();
    setToken(null);
    setUser(null);
  }, []);

  const value = {
    user,
    token,
    loading,
    isAuthenticated: Boolean(token),
    login,
    signup,
    logout
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
