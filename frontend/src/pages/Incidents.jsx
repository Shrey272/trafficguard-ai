import React from 'react';
import { useNavigate } from 'react-router-dom';
import { TrendingUp, TrendingDown, Eye, Calendar, ChevronDown, MoreVertical, Car, AlertTriangle } from 'lucide-react';
import { useRealtime } from '../context/RealtimeContext';

const Incidents = () => {
  const navigate = useNavigate();
  const { incidents } = useRealtime();

  const handleRowClick = (id) => {
    navigate(`/incidents/${id}`);
  };

  return (
    <div className="flex flex-col gap-6 max-w-7xl mx-auto h-full">
      {/* Header */}
      <div className="flex justify-between items-end">
        <div>
          <h2 className="text-2xl font-bold text-white mb-1">Incident History</h2>
          <p className="text-slate-400 text-sm">Review and analyze past traffic anomalies, accidents, and AI detections.</p>
        </div>
      </div>

      {/* Top Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-dark-panel border border-dark-border rounded-lg p-5 flex flex-col justify-between">
          <div className="flex justify-between items-start mb-4">
            <h3 className="text-slate-400 text-xs font-bold tracking-wider">TOTAL INCIDENTS THIS WEEK</h3>
            <TrendingUp size={16} className="text-slate-500" />
          </div>
          <div className="flex items-baseline gap-3">
            <div className="text-4xl font-bold text-white">{incidents.length}</div>
            <div className="flex items-center text-emerald-400 text-sm font-semibold"><TrendingUp size={14} className="mr-1"/> Live</div>
          </div>
        </div>

        <div className="bg-dark-panel border border-dark-border rounded-lg p-5 flex flex-col justify-between">
          <div className="flex justify-between items-start mb-4">
            <h3 className="text-slate-400 text-xs font-bold tracking-wider">AVG RESPONSE TIME</h3>
            <div className="w-4 h-4 rounded-full border-2 border-slate-500 border-t-transparent animate-spin"></div>
          </div>
          <div className="flex items-baseline gap-3">
            <div className="text-4xl font-bold text-white">4m 12s</div>
            <div className="flex items-center text-emerald-400 text-sm font-semibold"><TrendingUp size={14} className="mr-1"/> 12%</div>
          </div>
        </div>

        <div className="bg-dark-panel border border-dark-border rounded-lg p-5 flex flex-col justify-between">
          <div className="flex justify-between items-start mb-4">
            <h3 className="text-slate-400 text-xs font-bold tracking-wider">DETECTION ACCURACY</h3>
            <Eye size={16} className="text-slate-500" />
          </div>
          <div className="flex items-baseline gap-3">
            <div className="text-4xl font-bold text-white">98.4%</div>
            <div className="text-sm text-slate-500 font-semibold">AI Confidence</div>
          </div>
        </div>
      </div>

      {/* Filter Bar */}
      <div className="bg-dark-panel border border-dark-border rounded-lg p-4 flex justify-between items-center">
        <div className="flex items-center gap-6">
          <button className="flex items-center gap-2 text-slate-300 text-sm hover:text-white transition-colors">
            <Calendar size={16} /> Last 7 Days <ChevronDown size={14} />
          </button>
          
          <div className="flex items-center gap-3 border-l border-dark-border pl-6">
            <span className="text-slate-400 text-sm">Severity:</span>
            <div className="flex bg-dark-sidebar border border-dark-border rounded p-1">
              <button className="px-4 py-1 text-xs text-slate-400 hover:text-white rounded transition-colors">All</button>
              <button className="px-4 py-1 text-xs bg-rose-500/20 text-rose-400 rounded font-semibold transition-colors">Major</button>
              <button className="px-4 py-1 text-xs text-amber-400 hover:bg-amber-500/10 rounded transition-colors">Mod</button>
              <button className="px-4 py-1 text-xs text-slate-400 hover:text-white rounded transition-colors">Minor</button>
            </div>
          </div>
        </div>
        
        <div className="flex gap-4">
          <button className="flex items-center gap-2 text-slate-300 text-sm hover:text-white border-b border-dark-border pb-1">
            All Types <ChevronDown size={14} />
          </button>
          <button className="flex items-center gap-2 text-slate-300 text-sm hover:text-white border-b border-dark-border pb-1">
            All Status <ChevronDown size={14} />
          </button>
        </div>
      </div>

      {/* Table */}
      <div className="bg-dark-panel border border-dark-border rounded-lg overflow-hidden flex-1 flex flex-col">
        <div className="overflow-x-auto flex-1">
          <table className="w-full text-sm text-left whitespace-nowrap">
            <thead className="text-[10px] text-slate-500 uppercase bg-dark-sidebar/50 border-b border-dark-border">
              <tr>
                <th className="px-6 py-4 font-medium">ID</th>
                <th className="px-6 py-4 font-medium">Date & Time</th>
                <th className="px-6 py-4 font-medium">Location</th>
                <th className="px-6 py-4 font-medium">Type</th>
                <th className="px-6 py-4 font-medium">Severity</th>
                <th className="px-6 py-4 font-medium">AI Conf.</th>
                <th className="px-6 py-4 font-medium">Vehicles</th>
                <th className="px-6 py-4 font-medium">Status</th>
                <th className="px-6 py-4 font-medium text-right">Action</th>
              </tr>
            </thead>
            <tbody className="text-slate-300">
              {incidents.map((inc) => (
                <tr 
                  key={inc.id}
                  className="border-b border-dark-border/50 hover:bg-slate-800/50 cursor-pointer transition-colors"
                  onClick={() => handleRowClick(inc.id)}
                >
                  <td className="px-6 py-4 text-slate-400">TG-{inc.id}</td>
                  <td className="px-6 py-4">
                    <div className="text-white">{new Date(inc.timestamp).toLocaleDateString()}</div>
                    <div className="text-slate-500 text-xs">{new Date(inc.timestamp).toLocaleTimeString()}</div>
                  </td>
                  <td className="px-6 py-4">{inc.camera_id}</td>
                  <td className={`px-6 py-4 flex items-center gap-2 ${inc.incident_type === 'ACCIDENT' ? 'text-rose-400' : 'text-amber-400'}`}>
                    {inc.incident_type === 'ACCIDENT' ? <><Car size={16}/> Accident</> : <><TrendingDown size={16}/> Congestion</>}
                  </td>
                  <td className="px-6 py-4">
                    <span className={`border px-3 py-1 rounded-full text-[10px] font-bold tracking-wider ${
                      inc.severity === 'Major' ? 'border-rose-500/50 text-rose-400 bg-rose-500/10' :
                      inc.severity === 'Moderate' ? 'border-amber-500/50 text-amber-400 bg-amber-500/10' :
                      'border-slate-500/50 text-slate-400'
                    }`}>
                      {inc.severity.toUpperCase()}
                    </span>
                  </td>
                  <td className="px-6 py-4">{inc.confidence}%</td>
                  <td className="px-6 py-4">{inc.vehicle_count}</td>
                  <td className="px-6 py-4">
                    <span className={`border px-2 py-1 rounded text-[10px] font-bold ${
                      inc.status === 'NEW' ? 'border-amber-500/50 text-amber-400' : 'border-emerald-500/50 text-emerald-400'
                    }`}>
                      {inc.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-right"><button className="text-slate-500 hover:text-white"><MoreVertical size={18} /></button></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        
        {/* Pagination */}
        <div className="p-4 border-t border-dark-border flex justify-between items-center text-xs text-slate-500">
          <div>Showing {Math.min(1, incidents.length)} to {Math.min(10, incidents.length)} of {incidents.length} entries (Live)</div>
          <div className="flex">
            <button className="px-3 py-1 border border-dark-border rounded-l hover:bg-slate-800">&lt;</button>
            <button className="px-3 py-1 border-t border-b border-dark-border bg-indigo-500/20 text-indigo-400">1</button>
            <button className="px-3 py-1 border border-dark-border hover:bg-slate-800">2</button>
            <button className="px-3 py-1 border-t border-b border-r border-dark-border hover:bg-slate-800">3</button>
            <button className="px-3 py-1 border-t border-b border-r border-dark-border hover:bg-slate-800">...</button>
            <button className="px-3 py-1 border border-l-0 border-dark-border rounded-r hover:bg-slate-800">&gt;</button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Incidents;
