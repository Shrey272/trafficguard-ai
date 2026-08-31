import React from 'react';
import { NavLink } from 'react-router-dom';
import { LayoutDashboard, Video, Map as MapIcon, AlertTriangle, BarChart2, PlusSquare, Settings, Shield, FileText } from 'lucide-react';

const Sidebar = ({ isOpen, setIsOpen }) => {
  const navItems = [
    { name: 'Dashboard', icon: LayoutDashboard, path: '/' },
    { name: 'Live Cameras', icon: Video, path: '/cameras' },
    { name: 'ANPR & Vehicle Trace', icon: FileText, path: '/anpr' },
    { name: 'Map', icon: MapIcon, path: '/map' },
    { name: 'Incidents', icon: AlertTriangle, path: '/incidents', badge: 3 },
    { name: 'Analytics', icon: BarChart2, path: '/analytics' },
    { name: 'Hospitals', icon: PlusSquare, path: '/hospitals' },
  ];


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
            <div className="bg-slate-700/50 p-2 rounded-lg text-slate-300">
              <Shield size={20} />
            </div>
            <div>
              <h1 className="text-white font-bold tracking-wide text-sm">Command Center</h1>
              <p className="text-xs text-slate-400">V2.4.0-ACTIVE</p>
            </div>
          </div>
        </div>
        
        {/* Nav Links */}
        <nav className="p-4 space-y-1">
          {navItems.map((item) => (
            <NavLink
              key={item.name}
              to={item.path}
              className={({ isActive }) =>
                `flex items-center justify-between px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                  isActive
                    ? 'bg-slate-800/60 text-white'
                    : 'text-slate-400 hover:bg-slate-800/40 hover:text-white'
                }`
              }
            >
              <div className="flex items-center gap-3">
                <item.icon size={18} />
                <span>{item.name}</span>
              </div>
              {item.badge && (
                <span className="bg-rose-500/20 text-rose-400 text-xs px-2 py-0.5 rounded-md font-semibold">
                  {item.badge}
                </span>
              )}
            </NavLink>
          ))}
        </nav>
      </div>

      {/* Footer Nav */}
      <div className="p-4 border-t border-dark-border">
        <NavLink
          to="/settings"
          className="flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium text-slate-400 hover:bg-slate-800/40 hover:text-white transition-colors"
        >
          <Settings size={18} />
          <span>Settings</span>
        </NavLink>
      </div>
    </aside>
    </>
  );
};

export default Sidebar;
