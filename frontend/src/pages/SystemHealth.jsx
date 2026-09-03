import React, { useState, useEffect } from 'react';
import { Activity, Server, Database, Video, AlertTriangle, Users, Power, RefreshCw } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

const SystemHealth = () => {
  const { authFetch } = useAuth();
  const [healthData, setHealthData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lastUpdated, setLastUpdated] = useState(null);

  const fetchHealth = async () => {
    try {
      setLoading(true);
      setError(null);
      const res = await authFetch('/api/system/health');
      if (res.ok) {
        const data = await res.json();
        setHealthData(data);
        setLastUpdated(new Date().toLocaleTimeString());
      } else {
        const text = await res.text();
        setError(`Error ${res.status}: ${text}`);
      }
    } catch (err) {
      console.error("Failed to fetch system health", err);
      setError(err.message || "Network error");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHealth();
    const interval = setInterval(fetchHealth, 15000); // refresh every 15s
    return () => clearInterval(interval);
  }, []);

  if (!healthData && loading) {
    return (
      <div className="flex h-full items-center justify-center text-slate-400">
        <RefreshCw className="animate-spin mr-3" /> Loading health data...
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6 h-full text-rose-400">
        <h2 className="text-xl font-bold mb-2">Failed to load system health</h2>
        <pre className="bg-slate-900 p-4 rounded text-sm overflow-auto">{error}</pre>
        <button onClick={fetchHealth} className="mt-4 px-4 py-2 bg-slate-800 rounded">Retry</button>
      </div>
    );
  }

  if (!healthData) {
     return <div className="p-6 text-white">No data returned</div>;
  }

  const StatusBadge = ({ status }) => {
    const isUp = status === 'UP';
    return (
      <span className={`px-2 py-1 rounded text-xs font-bold font-mono ${isUp ? 'bg-emerald-500/20 text-emerald-400' : 'bg-rose-500/20 text-rose-400'}`}>
        {status}
      </span>
    );
  };

  return (
    <div className="p-6 h-full overflow-y-auto">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-2xl font-bold text-white flex items-center gap-2">
            <Activity className="text-blue-500" /> System Health
          </h1>
          <p className="text-slate-400 text-sm mt-1">Platform operational status and telemetry</p>
        </div>
        <div className="flex items-center gap-4 text-sm">
          <span className="text-slate-400">Last updated: <span className="text-white font-mono">{lastUpdated}</span></span>
          <button 
            onClick={fetchHealth}
            className="flex items-center gap-2 px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg transition-colors border border-slate-700"
          >
            <RefreshCw size={14} className={loading ? 'animate-spin' : ''} />
            Refresh
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        
        {/* Core Platform */}
        <div className="bg-dark-panel rounded-xl border border-dark-border p-5">
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-white font-semibold flex items-center gap-2"><Server size={18} className="text-purple-400" /> Core Platform</h3>
            <StatusBadge status={healthData?.status} />
          </div>
          <div className="space-y-3">
            <div className="flex justify-between items-center p-3 bg-slate-800/40 rounded-lg">
              <span className="text-slate-400 text-sm flex items-center gap-2"><Database size={16}/> Database (PostgreSQL)</span>
              <StatusBadge status={healthData?.database} />
            </div>
            <div className="flex justify-between items-center p-3 bg-slate-800/40 rounded-lg">
              <span className="text-slate-400 text-sm flex items-center gap-2"><Users size={16}/> Active WebSockets</span>
              <span className="text-white font-mono font-bold">{healthData?.websockets?.active_connections || 0}</span>
            </div>
          </div>
        </div>

        {/* Camera Infrastructure */}
        <div className="bg-dark-panel rounded-xl border border-dark-border p-5">
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-white font-semibold flex items-center gap-2"><Video size={18} className="text-blue-400" /> Camera Infrastructure</h3>
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div className="p-3 bg-slate-800/40 rounded-lg text-center">
              <div className="text-2xl font-bold text-white mb-1">{healthData?.cameras?.total || 0}</div>
              <div className="text-xs text-slate-400 uppercase tracking-wider">Total</div>
            </div>
            <div className="p-3 bg-slate-800/40 rounded-lg text-center border-b-2 border-emerald-500/50">
              <div className="text-2xl font-bold text-emerald-400 mb-1">{healthData?.cameras?.online || 0}</div>
              <div className="text-xs text-slate-400 uppercase tracking-wider">Online</div>
            </div>
            <div className="p-3 bg-slate-800/40 rounded-lg text-center border-b-2 border-slate-500/50">
              <div className="text-2xl font-bold text-slate-400 mb-1">{healthData?.cameras?.offline || 0}</div>
              <div className="text-xs text-slate-400 uppercase tracking-wider">Offline</div>
            </div>
            <div className="p-3 bg-slate-800/40 rounded-lg text-center border-b-2 border-rose-500/50">
              <div className="text-2xl font-bold text-rose-400 mb-1">{healthData?.cameras?.error || 0}</div>
              <div className="text-xs text-slate-400 uppercase tracking-wider">Error</div>
            </div>
          </div>
        </div>

        {/* Edge Workers */}
        <div className="bg-dark-panel rounded-xl border border-dark-border p-5">
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-white font-semibold flex items-center gap-2"><Power size={18} className="text-emerald-400" /> Edge Processing</h3>
            <span className="text-xs font-mono bg-blue-500/20 text-blue-400 px-2 py-1 rounded">REDIS PUB/SUB</span>
          </div>
          <div className="space-y-3">
            <div className="flex justify-between items-center p-3 bg-slate-800/40 rounded-lg">
              <span className="text-slate-400 text-sm">Active Workers</span>
              <span className="text-emerald-400 font-mono font-bold text-lg">{healthData?.edge_workers?.active || 0}</span>
            </div>
            <div className="flex justify-between items-center p-3 bg-slate-800/40 rounded-lg">
              <span className="text-slate-400 text-sm">Offline Workers</span>
              <span className="text-rose-400 font-mono font-bold text-lg">{healthData?.edge_workers?.offline || 0}</span>
            </div>
          </div>
        </div>

        {/* Analytics Pipeline */}
        <div className="bg-dark-panel rounded-xl border border-dark-border p-5">
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-white font-semibold flex items-center gap-2"><AlertTriangle size={18} className="text-amber-400" /> AI Pipeline</h3>
          </div>
          <div className="p-4 bg-amber-500/10 border border-amber-500/20 rounded-lg flex items-center justify-between">
            <div>
              <div className="text-sm font-semibold text-amber-500">Unresolved Incidents</div>
              <div className="text-xs text-slate-400 mt-1">Pending operator review</div>
            </div>
            <div className="text-3xl font-bold text-amber-400 font-mono">{healthData?.incidents?.active || 0}</div>
          </div>
        </div>

      </div>
    </div>
  );
};

export default SystemHealth;
