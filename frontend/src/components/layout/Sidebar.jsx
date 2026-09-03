import React from 'react';
import { NavLink } from 'react-router-dom';
import { 
  LayoutDashboard, Video, Server, Map as MapIcon, 
  AlertTriangle, BarChart2, PlusSquare, Settings, 
  Shield, FileText, Activity, ShieldCheck
} from 'lucide-react';
import { useAuth } from '../../context/AuthContext';

const Sidebar = ({ isOpen, setIsOpen }) => {
  const { user, isAdmin } = useAuth();

  const navItems = [
    { name: 'Dashboard', icon: LayoutDashboard, path: '/' },
    { name: 'Live CCTV Grid', icon: Video, path: '/cameras' },
    { name: 'Camera Registry', icon: Server, path: '/cameras/manage' },
    { name: 'GIS Traffic Map', icon: MapIcon, path: '/map' },
    { name: 'ANPR & Vehicle Trace', icon: FileText, path: '/anpr' },
    { name: 'Watchlist Management', icon: Shield, path: '/watchlist' },
    { name: 'Incidents', icon: AlertTriangle, path: '/incidents' },
    { name: 'Analytics', icon: BarChart2, path: '/analytics' },
    { name: 'Hospitals', icon: PlusSquare, path: '/hospitals' },
  ];

  if (isAdmin) {
    navItems.push({ name: 'System Audit Logs', icon: ShieldCheck, path: '/audit-logs' });
    navItems.push({ name: 'System Health', icon: Activity, path: '/system-health' });
  }

  return (
    <>
      {/* Mobile overlay */}
      {isOpen && (
        <div 
          className="fixed inset-0 bg-black/60 z-40 md:hidden"
          onClick={() => setIsOpen(false)}
        />
      )}
      <aside className={`fixed md:static inset-y-0 left-0 z-50 w-64 bg-dark-sidebar border-r border-dark-border flex flex-col justify-between transform transition-transform duration-300 ease-in-out ${isOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0'}`}>
        <div>
          {/* Brand */}
          <div className="h-16 flex items-center px-6 border-b border-dark-border">
            <div className="flex items-center gap-3">
              <div className="bg-blue-600/20 p-2 rounded-lg text-blue-400 border border-blue-500/30">
                <Shield size={20} />
              </div>
              <div>
                <h1 className="text-white font-bold tracking-wide text-sm">TrafficGuard AI</h1>
                <p className="text-[10px] text-emerald-400 font-mono flex items-center gap-1">
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></span> V2.4.0-PHASE1
                </p>
              </div>
            </div>
          </div>
          
          {/* Nav Links */}
          <nav className="p-4 space-y-1">
            {navItems.map((item) => (
              <NavLink
                key={item.name}
                to={item.path}
                onClick={() => setIsOpen && setIsOpen(false)}
                className={({ isActive }) =>
                  `flex items-center justify-between px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                    isActive
                      ? 'bg-blue-600/20 text-blue-400 border border-blue-500/30'
                      : 'text-slate-400 hover:bg-slate-800/40 hover:text-white'
                  }`
                }
              >
                <div className="flex items-center gap-3">
                  <item.icon size={18} />
                  <span>{item.name}</span>
                </div>
              </NavLink>
            ))}
          </nav>
        </div>

        {/* User Role Card */}
        <div className="p-4 border-t border-dark-border bg-dark-panel/40 m-2 rounded-xl">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-blue-600 to-indigo-600 flex items-center justify-center text-white text-xs font-bold font-mono">
              {user?.username ? user.username.substring(0, 2).toUpperCase() : 'US'}
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-xs font-semibold text-white truncate">{user?.username || 'Guest'}</p>
              <span className={`text-[10px] font-bold uppercase px-1.5 py-0.2 rounded font-mono ${
                user?.role === 'ADMIN' ? 'bg-purple-500/20 text-purple-400' :
                user?.role === 'OPERATOR' ? 'bg-blue-500/20 text-blue-400' :
                'bg-slate-700 text-slate-300'
              }`}>
                {user?.role || 'VIEWER'}
              </span>
            </div>
          </div>
        </div>
      </aside>
    </>
  );
};

export default Sidebar;
