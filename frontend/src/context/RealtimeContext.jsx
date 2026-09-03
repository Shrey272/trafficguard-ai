import React, { createContext, useContext, useEffect, useState } from 'react';
import { useAuth } from './AuthContext';

const RealtimeContext = createContext(null);

export const useRealtime = () => {
  return useContext(RealtimeContext);
};

export const RealtimeProvider = ({ children }) => {
  const auth = useAuth();
  const [incidents, setIncidents] = useState([]);
  const [isConnected, setIsConnected] = useState(false);
  const [lastIncident, setLastIncident] = useState(null);
  const [cameraHealthMap, setCameraHealthMap] = useState({});
  const [watchlistAlerts, setWatchlistAlerts] = useState([]);
  const [lastWatchlistAlert, setLastWatchlistAlert] = useState(null);

  useEffect(() => {
    // Initial fetch of historical incidents
    fetch('/api/incidents')
      .then(res => res.json())
      .then(data => {
        if (Array.isArray(data)) {
          setIncidents(data);
        }
      })
      .catch(err => console.error("Failed to fetch initial incidents:", err));

    // Connect Secure WebSocket
    let ws = null;
    let reconnectTimeout = null;

    const connectWs = () => {
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      const host = window.location.host;
      const tokenParam = auth?.token ? `?token=${encodeURIComponent(auth.token)}` : '';
      const wsUrl = `${protocol}//${host}/ws/alerts${tokenParam}`;
      
      try {
        ws = new WebSocket(wsUrl);

        ws.onopen = () => {
          console.log('Connected to secure real-time WebSocket');
          setIsConnected(true);
        };

        ws.onmessage = (event) => {
          try {
            const message = JSON.parse(event.data);
            
            if (message.type === 'NEW_INCIDENT') {
              const newIncident = message.data;
              setLastIncident(newIncident);
              setIncidents(prev => [newIncident, ...prev]);
            } else if (message.type === 'INCIDENT_STATUS_CHANGED') {
              const updated = message.data;
              setIncidents(prev => prev.map(inc => inc.id === updated.id ? { ...inc, status: updated.status } : inc));
            } else if (message.type === 'WATCHLIST_ALERT') {
              const newAlert = message.data;
              setLastWatchlistAlert(newAlert);
              setWatchlistAlerts(prev => [newAlert, ...prev]);
            } else if (message.type === 'CAMERA_HEALTH_METRICS') {
              const metricsArray = message.data;
              if (Array.isArray(metricsArray)) {
                setCameraHealthMap(prev => {
                  const updatedMap = { ...prev };
                  metricsArray.forEach(m => {
                    updatedMap[m.camera_id] = m;
                    if (m.camera_code) {
                      updatedMap[m.camera_code] = m;
                    }
                  });
                  return updatedMap;
                });
              }
            }
          } catch (e) {
            console.error("Error parsing websocket message", e);
          }
        };

        ws.onclose = () => {
          setIsConnected(false);
          reconnectTimeout = setTimeout(connectWs, 4000);
        };

        ws.onerror = (error) => {
          console.warn('WebSocket error:', error);
          if (ws) ws.close();
        };
      } catch (err) {
        console.error("WebSocket connection setup error:", err);
      }
    };

    connectWs();

    return () => {
      if (reconnectTimeout) clearTimeout(reconnectTimeout);
      if (ws) ws.close();
    };
  }, [auth?.token]);

  return (
    <RealtimeContext.Provider value={{
      incidents,
      isConnected,
      lastIncident,
      cameraHealthMap,
      watchlistAlerts,
      lastWatchlistAlert
    }}>
      {children}
    </RealtimeContext.Provider>
  );
};
