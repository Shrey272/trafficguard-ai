import React from 'react';
import { MapContainer, TileLayer, Marker, Popup, ZoomControl } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import { Plus, Minus, Focus, Navigation } from 'lucide-react';

const MapView = () => {
  return (
    <div className="flex h-full gap-4 relative -m-4 md:-m-6">
      {/* Map Area */}
      <div className="flex-1 relative z-0">
        <MapContainer 
          center={[44.4268, 26.1025]} 
          zoom={13} 
          style={{ height: '100%', width: '100%', background: '#121621' }}
          zoomControl={false}
        >
          <TileLayer
            url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'
          />
        </MapContainer>

        {/* Custom Map Controls Overlay */}
        <div className="absolute top-4 left-4 z-[400] flex flex-col gap-4">
          <div className="bg-dark-panel border border-dark-border rounded-lg shadow-lg flex flex-col w-48">
            <div className="flex justify-around border-b border-dark-border p-2">
              <button className="text-white hover:bg-slate-800 p-2 rounded transition-colors"><Plus size={20} /></button>
              <button className="text-white hover:bg-slate-800 p-2 rounded transition-colors"><Minus size={20} /></button>
            </div>
            <div className="p-4">
              <h4 className="text-xs font-semibold text-slate-400 mb-3 tracking-widest">MAP LEGEND</h4>
              <ul className="space-y-3 text-sm text-slate-300">
                <li className="flex items-center gap-3"><span className="w-2.5 h-2.5 rounded-full bg-emerald-500"></span> Normal Flow</li>
                <li className="flex items-center gap-3"><span className="w-2.5 h-2.5 rounded-full bg-amber-500"></span> Congestion</li>
                <li className="flex items-center gap-3"><span className="w-2.5 h-2.5 rounded-full bg-rose-500"></span> Accident</li>
                <li className="flex items-center gap-3 text-slate-400"><Plus size={14} /> Medical</li>
                <li className="flex items-center gap-3 text-slate-400"><span className="font-serif italic text-xs">P</span> Police Dept</li>
              </ul>
            </div>
          </div>
        </div>
      </div>

      {/* Right Sidebar - Active Incidents */}
      <div className="w-80 bg-dark-sidebar border-l border-dark-border z-[400] h-full overflow-y-auto flex flex-col shadow-2xl absolute right-0 top-0 lg:relative">
        <div className="p-4 border-b border-dark-border flex justify-between items-center bg-dark-sidebar/95 sticky top-0 backdrop-blur-sm">
          <h3 className="text-rose-400 font-semibold flex items-center gap-2">
            <span className="text-2xl">✻</span> Active Incidents
          </h3>
          <span className="bg-rose-500/20 text-rose-400 border border-rose-500/30 text-xs px-2 py-0.5 rounded">3 ACTIVE</span>
        </div>

        <div className="p-4 space-y-4">
          {/* Incident Card - Critical */}
          <div className="bg-dark-panel border border-dark-border rounded-lg p-4">
            <div className="flex justify-between items-start mb-2">
              <span className="text-rose-400 text-xs font-bold tracking-wider flex items-center gap-1.5">
                <span className="w-1.5 h-1.5 bg-rose-500 rounded-full"></span> CRITICAL
              </span>
              <span className="text-xs text-slate-400">10:42 AM</span>
            </div>
            <h4 className="text-white font-medium mb-1">Multi-Vehicle Collision</h4>
            <p className="text-sm text-slate-400 mb-4 line-clamp-2">Adajan Patia, Surat. Lanes 1 & 2 blocked.</p>
            <div className="flex gap-2">
               <button className="flex-1 bg-slate-800 text-white text-xs py-1.5 rounded flex items-center justify-center gap-1 hover:bg-slate-700 transition-colors"><Focus size={14} /> Focus</button>
               <button className="flex-1 bg-indigo-600/20 text-indigo-400 border border-indigo-500/30 text-xs py-1.5 rounded flex items-center justify-center gap-1 hover:bg-indigo-600/30 transition-colors"><Navigation size={14} /> Dispatch</button>
            </div>
          </div>

          {/* Incident Card - Warning */}
          <div className="bg-dark-panel border border-dark-border rounded-lg p-4">
            <div className="flex justify-between items-start mb-2">
              <span className="text-amber-400 text-xs font-bold tracking-wider flex items-center gap-1.5">
                <span className="w-1.5 h-1.5 bg-amber-500 rounded-full"></span> WARNING
              </span>
              <span className="text-xs text-slate-400">10:15 AM</span>
            </div>
            <h4 className="text-white font-medium mb-1">Severe Congestion</h4>
            <p className="text-sm text-slate-400 mb-4 line-clamp-2">Ring Road Northbound. Average speed &lt; 15mph.</p>
            <div className="flex gap-2">
               <button className="w-full bg-slate-800 text-white text-xs py-1.5 rounded flex items-center justify-center gap-1 hover:bg-slate-700 transition-colors"><Focus size={14} /> Focus</button>
            </div>
          </div>

          {/* Incident Card - Info */}
          <div className="bg-dark-panel border border-dark-border rounded-lg p-4">
            <div className="flex justify-between items-start mb-2">
              <span className="text-slate-300 text-xs font-bold tracking-wider flex items-center gap-1.5">
                <span className="w-1.5 h-1.5 bg-slate-400 rounded-full"></span> INFO
              </span>
              <span className="text-xs text-slate-400">09:30 AM</span>
            </div>
            <h4 className="text-white font-medium mb-1">Signal Malfunction</h4>
            <p className="text-sm text-slate-400 mb-4 line-clamp-2">Pedestrian crossing signal out of sync at Udhana Darwaja.</p>
            <div className="flex gap-2">
               <button className="w-full bg-slate-800 text-white text-xs py-1.5 rounded flex items-center justify-center gap-1 hover:bg-slate-700 transition-colors"><Focus size={14} /> Focus</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default MapView;
