import React, { useState, useEffect } from 'react';
import { Shield, FileText, Search, Filter, RefreshCw, UserCheck, AlertCircle, Clock, Database } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

const AuditLogs = () => {
  const { authFetch, isAdmin, user } = useAuth();
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filterAction, setFilterAction] = useState('ALL');
  const [searchQuery, setSearchQuery] = useState('');

  const fetchLogs = async () => {
    try {
      setLoading(true);
      const res = await authFetch('/api/audit-logs');
      if (res.ok) {
        const data = await res.json();
        setLogs(data);
      }
    } catch (err) {
      console.error("Failed to load audit logs:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (isAdmin) {
      fetchLogs();
    }
  }, [isAdmin]);

  if (!isAdmin) {
    return (
      <div className="flex flex-col items-center justify-center h-full max-w-md mx-auto text-center p-6">
        <div className="p-4 bg-rose-500/10 text-rose-400 rounded-full mb-4">
          <Shield size={40} />
        </div>
        <h3 className="text-xl font-bold text-white mb-2">Admin Access Required</h3>
        <p className="text-slate-400 text-sm mb-6">
          System audit logs contain security-sensitive event trails and can only be inspected by users with the <strong className="text-white">ADMIN</strong> role.
        </p>
      </div>
    );
  }

  const filteredLogs = logs.filter(log => {
    const matchesSearch = 
      log.username?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      log.action?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      log.details?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      log.resource_type?.toLowerCase().includes(searchQuery.toLowerCase());
    
    const matchesAction = filterAction === 'ALL' || log.action === filterAction;
    return matchesSearch && matchesAction;
  });

  const getActionBadge = (action) => {
    if (action.includes('CREATED')) {
      return <span className="px-2 py-0.5 rounded text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">{action}</span>;
    } else if (action.includes('DELETED')) {
      return <span className="px-2 py-0.5 rounded text-xs font-semibold bg-rose-500/10 text-rose-400 border border-rose-500/20">{action}</span>;
    } else if (action.includes('CONNECTED')) {
      return <span className="px-2 py-0.5 rounded text-xs font-semibold bg-blue-500/10 text-blue-400 border border-blue-500/20">{action}</span>;
    } else if (action.includes('DISCONNECTED')) {
      return <span className="px-2 py-0.5 rounded text-xs font-semibold bg-amber-500/10 text-amber-400 border border-amber-500/20">{action}</span>;
    } else if (action.includes('LOGIN')) {
      return <span className="px-2 py-0.5 rounded text-xs font-semibold bg-purple-500/10 text-purple-400 border border-purple-500/20">{action}</span>;
    }
    return <span className="px-2 py-0.5 rounded text-xs font-semibold bg-slate-800 text-slate-300 border border-dark-border">{action}</span>;
  };

  return (
    <div className="flex flex-col gap-6 max-w-7xl mx-auto h-full">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <div className="flex items-center gap-2">
            <h2 className="text-2xl font-bold text-white">System Audit Trail</h2>
            <span className="bg-purple-500/10 text-purple-400 border border-purple-500/20 text-xs px-2.5 py-0.5 rounded-full font-semibold">
              COMPLIANCE LOGS
            </span>
          </div>
          <p className="text-slate-400 text-sm mt-1">
            Immutable tracking for logins, camera mutations, stream states, and incident handling.
          </p>
        </div>

        <button
          onClick={fetchLogs}
          className="p-2 bg-dark-panel border border-dark-border text-slate-300 hover:text-white rounded-lg transition-colors flex items-center gap-2 text-sm"
        >
          <RefreshCw size={16} className={loading ? 'animate-spin' : ''} />
          <span>Refresh</span>
        </button>
      </div>

      {/* Filter Bar */}
      <div className="bg-dark-panel border border-dark-border rounded-xl p-4 flex flex-col md:flex-row gap-3 items-center justify-between">
        <div className="relative w-full md:w-80">
          <Search size={18} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
          <input
            type="text"
            placeholder="Search action, user, details..."
            value={searchQuery}
            onChange={e => setSearchQuery(e.target.value)}
            className="w-full bg-dark-sidebar border border-dark-border rounded-lg pl-9 pr-3 py-2 text-sm text-white focus:outline-none focus:border-blue-500 placeholder-slate-500"
          />
        </div>

        <div className="flex items-center gap-3 w-full md:w-auto">
          <span className="text-xs text-slate-400">Action:</span>
          <select
            value={filterAction}
            onChange={e => setFilterAction(e.target.value)}
            className="bg-dark-sidebar border border-dark-border rounded-lg px-3 py-2 text-xs text-white focus:outline-none focus:border-blue-500"
          >
            <option value="ALL">All Actions</option>
            <option value="LOGIN">LOGIN</option>
            <option value="CAMERA_CREATED">CAMERA_CREATED</option>
            <option value="CAMERA_UPDATED">CAMERA_UPDATED</option>
            <option value="CAMERA_DELETED">CAMERA_DELETED</option>
            <option value="CAMERA_CONNECTED">CAMERA_CONNECTED</option>
            <option value="CAMERA_DISCONNECTED">CAMERA_DISCONNECTED</option>
            <option value="CAMERA_RESTARTED">CAMERA_RESTARTED</option>
            <option value="INCIDENT_ACKNOWLEDGED">INCIDENT_ACKNOWLEDGED</option>
            <option value="INCIDENT_RESOLVED">INCIDENT_RESOLVED</option>
          </select>
        </div>
      </div>

      {/* Logs Table */}
      <div className="bg-dark-panel border border-dark-border rounded-xl overflow-hidden flex-1 shadow-xl">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm text-slate-300">
            <thead className="bg-dark-sidebar border-b border-dark-border text-xs text-slate-400 uppercase tracking-wider font-semibold">
              <tr>
                <th className="px-4 py-3.5">Timestamp</th>
                <th className="px-4 py-3.5">Action</th>
                <th className="px-4 py-3.5">User / Role</th>
                <th className="px-4 py-3.5">Target Resource</th>
                <th className="px-4 py-3.5">Event Details</th>
                <th className="px-4 py-3.5 text-right">IP Address</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-dark-border">
              {filteredLogs.length === 0 ? (
                <tr>
                  <td colSpan="6" className="px-4 py-12 text-center text-slate-500">
                    {loading ? "Loading audit logs..." : "No audit records found."}
                  </td>
                </tr>
              ) : (
                filteredLogs.map((log) => (
                  <tr key={log.id} className="hover:bg-slate-800/30 transition-colors">
                    <td className="px-4 py-3.5 whitespace-nowrap text-xs text-slate-400 font-mono">
                      {new Date(log.timestamp).toLocaleString()}
                    </td>
                    <td className="px-4 py-3.5 whitespace-nowrap">
                      {getActionBadge(log.action)}
                    </td>
                    <td className="px-4 py-3.5 whitespace-nowrap">
                      <div className="font-semibold text-white text-xs">{log.username}</div>
                      <div className="text-[11px] text-slate-400 font-mono">{log.role}</div>
                    </td>
                    <td className="px-4 py-3.5 whitespace-nowrap">
                      <span className="text-xs font-mono text-indigo-400 bg-indigo-500/10 px-2 py-0.5 rounded">
                        {log.resource_type} {log.resource_id ? `#${log.resource_id}` : ''}
                      </span>
                    </td>
                    <td className="px-4 py-3.5">
                      <p className="text-xs text-slate-300 line-clamp-2">{log.details || 'N/A'}</p>
                    </td>
                    <td className="px-4 py-3.5 whitespace-nowrap text-right font-mono text-xs text-slate-400">
                      {log.ip_address || '127.0.0.1'}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default AuditLogs;
