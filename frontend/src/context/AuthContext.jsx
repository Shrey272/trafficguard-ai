import React, { createContext, useContext, useState, useEffect } from 'react';

const AuthContext = createContext(null);

export const useAuth = () => {
  return useContext(AuthContext);
};

export const AuthProvider = ({ children }) => {
  // Initialize with admin by default or from localStorage
  const [token, setToken] = useState(() => localStorage.getItem('tg_token') || null);
  const [user, setUser] = useState(() => {
    const saved = localStorage.getItem('tg_user');
    if (saved) {
      try { return JSON.parse(saved); } catch (e) { return null; }
    }
    // Default demo user: Admin
    return {
      id: 1,
      username: "admin",
      email: "admin@trafficguard.ai",
      role: "ADMIN",
      department: "Traffic HQ & Command"
    };
  });
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    // If token exists, verify or fetch profile
    if (token) {
      fetch('/api/auth/me', {
        headers: { 'Authorization': `Bearer ${token}` }
      })
        .then(res => {
          if (res.ok) return res.json();
          throw new Error("Token invalid");
        })
        .then(userData => {
          setUser(userData);
          localStorage.setItem('tg_user', JSON.stringify(userData));
        })
        .catch(() => {
          // If token fails, clear or keep mock user
        });
    }
  }, [token]);

  const login = async (username, password) => {
    setLoading(true);
    try {
      const res = await fetch('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password })
      });

      if (!res.ok) {
        const errorData = await res.json().catch(() => ({ detail: 'Authentication failed' }));
        throw new Error(errorData.detail || 'Authentication failed');
      }

      const data = await res.json();
      setToken(data.access_token);
      setUser(data.user);
      localStorage.setItem('tg_token', data.access_token);
      localStorage.setItem('tg_user', JSON.stringify(data.user));
      return { success: true, user: data.user };
    } catch (err) {
      return { success: false, error: err.message };
    } finally {
      setLoading(false);
    }
  };

  const logout = () => {
    setToken(null);
    setUser({
      id: 3,
      username: "viewer",
      email: "viewer@trafficguard.ai",
      role: "VIEWER",
      department: "Public Safety & City Audit"
    });
    localStorage.removeItem('tg_token');
    localStorage.removeItem('tg_user');
  };

  // Quick switcher for development & testing
  const switchAccount = async (targetUsername, targetPassword) => {
    return await login(targetUsername, targetPassword);
  };

  const hasRole = (allowedRoles) => {
    if (!user || !user.role) return false;
    return allowedRoles.includes(user.role);
  };

  const authFetch = (url, options = {}) => {
    const headers = { ...options.headers };
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }
    return fetch(url, { ...options, headers });
  };

  return (
    <AuthContext.Provider value={{
      user,
      token,
      loading,
      login,
      logout,
      switchAccount,
      hasRole,
      authFetch,
      isAdmin: user?.role === 'ADMIN',
      isOperator: user?.role === 'OPERATOR' || user?.role === 'ADMIN',
      isViewer: user?.role === 'VIEWER'
    }}>
      {children}
    </AuthContext.Provider>
  );
};
