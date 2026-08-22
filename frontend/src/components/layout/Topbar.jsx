import React from 'react';
import { useLocation } from 'react-router-dom';
import { Bell, Clock, Search } from 'lucide-react';

const Topbar = () => {
  const location = useLocation();
  
  // Format the path to a readable title
  const getPageTitle = () => {
    if (location.pathname === '/') return 'Dashboard';
    const path = location.pathname.split('/')[1];
    return path.charAt(0).toUpperCase() + path.slice(1).replace('-', ' ');
  };

  return (
    <header className="h-16 bg-dark-bg border-b border-dark-border flex items-center justify-between px-6 z-10 shrink-0">
      <div className="flex items-center gap-4">
        <h2 className="text-lg font-semibold text-white">TrafficGuard AI</h2>
        <span className="text-slate-500">/</span>
        <span className="text-slate-300 text-sm">{getPageTitle()}</span>
        <div className="ml-4 flex items-center gap-2 bg-emerald-950/30 text-emerald-400 px-3 py-1 rounded-full border border-emerald-900/50">
          <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></div>
          <span className="text-xs font-semibold tracking-wider">MONITORING ACTIVE</span>
        </div>
      </div>

      <div className="flex items-center gap-5 text-slate-400">
        <div className="relative">
          <Search size={18} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
          <input 
            type="text" 
            placeholder="Search coordinates, units..." 
            className="bg-dark-sidebar border border-dark-border rounded-lg pl-10 pr-4 py-1.5 text-sm text-white focus:outline-none focus:border-slate-500 w-64 placeholder-slate-500"
          />
        </div>
        <button className="relative hover:text-white transition-colors">
          <Bell size={20} />
          <span className="absolute -top-1 -right-1 w-2 h-2 bg-rose-500 rounded-full"></span>
        </button>
        <button className="hover:text-white transition-colors">
          <Clock size={20} />
        </button>
        <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-blue-600 to-indigo-600 border border-slate-600 cursor-pointer overflow-hidden opacity-90 hover:opacity-100 transition-opacity">
           {/* Placeholder for user avatar */}
           <img src="https://api.dicebear.com/7.x/avataaars/svg?seed=Felix&backgroundColor=transparent" alt="User Avatar" />
        </div>
      </div>
    </header>
  );
};

export default Topbar;
