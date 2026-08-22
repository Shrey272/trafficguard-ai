import React, { createContext, useContext, useEffect, useState } from 'react';

const RealtimeContext = createContext(null);

export const useRealtime = () => {
  return useContext(RealtimeContext);
};

export const RealtimeProvider = ({ children }) => {
  const [incidents, setIncidents] = useState([]);
  const [isConnected, setIsConnected] = useState(false);
  const [lastIncident, setLastIncident] = useState(null);

  useEffect(() => {
    // Initial fetch of historical incidents
    fetch('/api/incidents')
      .then(res => res.json())
      .then(data => {
        setIncidents(data);
      })
      .catch(err => console.error("Failed to fetch initial incidents:", err));

    // Connect WebSocket
    const connectWs = () => {
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      const host = window.location.host; // includes port if present
      // In dev, Vite proxy might not proxy WS automatically unless configured, 
      // but Vite can proxy WebSockets if configured.
      const wsUrl = `${protocol}//${host}/ws/alerts`;
      const ws = new WebSocket(wsUrl);

      ws.onopen = () => {
        console.log('Connected to real-time alerts');
        setIsConnected(true);
      };

      ws.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data);
          if (message.type === 'NEW_INCIDENT') {
            const newIncident = message.data;
            setLastIncident(newIncident);
            setIncidents(prev => [newIncident, ...prev]);
          }
        } catch (e) {
          console.error("Error parsing websocket message", e);
        }
      };

      ws.onclose = () => {
        console.log('Disconnected from real-time alerts. Reconnecting in 5s...');
        setIsConnected(false);
        setTimeout(connectWs, 5000);
      };

      ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        ws.close();
      };

      return ws;
    };

    const wsInstance = connectWs();

    return () => {
      if (wsInstance) {
        wsInstance.close();
      }
    };
  }, []);

  return (
    <RealtimeContext.Provider value={{ incidents, isConnected, lastIncident }}>
      {children}
    </RealtimeContext.Provider>
  );
};
