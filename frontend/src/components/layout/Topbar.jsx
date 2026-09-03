import React, { useState } from 'react';
import { useLocation } from 'react-router-dom';
import { Bell, Clock, Search, Menu, Shield, User, ChevronDown, Check, LogOut } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { useRealtime } from '../../context/RealtimeContext';

const Topbar = ({ onMenuClick }) => {
  const location = useLocation();
  const { user, switchAccount, logout } = useAuth();
  const { isConnected } = useRealtime();
  const [roleDropdownOpen, setRoleDropdownOpen] = useState(false);

  const getPageTitle = () => {
    if (location.pathname === '/') return 'Command Dashboard';
    if (location.pathname === '/cameras/manage') return 'CCTV Camera Registry';
    if (location.pathname === '/cameras') return 'Live CCTV Feeds';
    if (location.pathname === '/map') return 'GIS Traffic Map';
    if (location.pathname === '/audit-logs') return 'System Audit Trail';
    const path = location.pathname.split('/')[1];
    return path.charAt(0).toUpperCase() + path.slice(1).replace('-', ' ');
  };

  const handleRoleSwitch = (username, pass) => {
    switchAccount(username, pass);
    setRoleDropdownOpen(false);
  };

  return (
    <header className="h-16 bg-dark-bg border-b border-dark-border flex items-center justify-between px-4 md:px-6 z-20 shrink-0">
      <div className="flex items-center gap-2 md:gap-4">
        <button className="md:hidden p-1 text-slate-400 hover:text-white" onClick={onMenuClick}>
          <Menu size={20} />
        </button>
        <h2 className="text-base md:text-lg font-semibold text-white truncate">TrafficGuard</h2>
        <span className="hidden sm:inline text-slate-500">/</span>
        <span className="hidden sm:inline text-slate-300 text-sm truncate font-medium">{getPageTitle()}</span>
        
        {/* Live WS Status */}
        <div className={`ml-1 md:ml-4 flex items-center gap-1.5 md:gap-2 px-2.5 py-1 rounded-full border text-xs font-semibold ${
          isConnected 
            ? 'bg-emerald-950/30 text-emerald-400 border-emerald-900/50' 
            : 'bg-rose-950/30 text-rose-400 border-rose-900/50'
        }`}>
          <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-emerald-500 animate-pulse' : 'bg-rose-500'}`}></div>
          <span className="text-[10px] md:text-xs tracking-wider hidden sm:inline">
            {isConnected ? 'STREAM TELEMETRY ACTIVE' : 'WS RECONNECTING'}
          </span>
        </div>
      </div>

      <div className="flex items-center gap-3 md:gap-4 text-slate-400">
        {/* Role Switcher Dropdown */}
        <div className="relative">
          <button
            onClick={() => setRoleDropdownOpen(!roleDropdownOpen)}
            className="flex items-center gap-2 bg-dark-panel hover:bg-slate-800 border border-dark-border px-3 py-1.5 rounded-lg text-xs text-white transition-colors"
          >
            <Shield size={14} className={
              user?.role === 'ADMIN' ? 'text-purple-400' :
              user?.role === 'OPERATOR' ? 'text-blue-400' : 'text-slate-400'
            } />
            <span className="font-semibold">{user?.username}</span>
            <span className="text-[10px] bg-slate-800 text-slate-300 px-1.5 py-0.5 rounded font-mono">
              {user?.role}
            </span>
            <ChevronDown size={14} className="text-slate-400" />
          </button>

          {roleDropdownOpen && (
            <div className="absolute right-0 mt-2 w-56 bg-dark-panel border border-dark-border rounded-xl shadow-2xl py-2 z-50 animate-in fade-in zoom-in-95">
              <div className="px-3 py-1.5 border-b border-dark-border mb-1">
                <p className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">Fast Role Switcher</p>
              </div>

              <button
                onClick={() => handleRoleSwitch('admin', 'admin123')}
                className={`w-full text-left px-3 py-2 text-xs flex items-center justify-between hover:bg-slate-800 transition-colors ${
                  user?.role === 'ADMIN' ? 'text-purple-400 font-bold bg-purple-500/10' : 'text-slate-300'
                }`}
              >
                <div>
                  <p className="font-semibold">Administrator (admin)</p>
                  <p className="text-[10px] text-slate-400">Full control, add/edit cameras, audit</p>
                </div>
                {user?.role === 'ADMIN' && <Check size={14} />}
              </button>

              <button
                onClick={() => handleRoleSwitch('operator', 'operator123')}
                className={`w-full text-left px-3 py-2 text-xs flex items-center justify-between hover:bg-slate-800 transition-colors ${
                  user?.role === 'OPERATOR' ? 'text-blue-400 font-bold bg-blue-500/10' : 'text-slate-300'
                }`}
              >
                <div>
                  <p className="font-semibold">Operator (operator)</p>
                  <p className="text-[10px] text-slate-400">Stream restart, connect, incidents</p>
                </div>
                {user?.role === 'OPERATOR' && <Check size={14} />}
              </button>

              <button
                onClick={() => handleRoleSwitch('viewer', 'viewer123')}
                className={`w-full text-left px-3 py-2 text-xs flex items-center justify-between hover:bg-slate-800 transition-colors ${
                  user?.role === 'VIEWER' ? 'text-slate-200 font-bold bg-slate-800' : 'text-slate-300'
                }`}
              >
                <div>
                  <p className="font-semibold">Viewer (viewer)</p>
                  <p className="text-[10px] text-slate-400">Read-only dashboard & map</p>
                </div>
                {user?.role === 'VIEWER' && <Check size={14} />}
              </button>

              <div className="border-t border-dark-border mt-1 pt-1">
                <button
                  onClick={() => {
                    logout();
                    setRoleDropdownOpen(false);
                  }}
                  className="w-full text-left px-3 py-1.5 text-xs text-rose-400 hover:bg-rose-500/10 flex items-center gap-2 transition-colors"
                >
                  <LogOut size={13} />
                  <span>Log Out</span>
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </header>
  );
};

export default Topbar;
