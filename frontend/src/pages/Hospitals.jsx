import React from 'react';
import { AlertTriangle, Bed, Users, CheckCircle } from 'lucide-react';
import { MapContainer, TileLayer, Polyline } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import { useRealtime } from '../context/RealtimeContext';

const Hospitals = () => {
  const { lastIncident } = useRealtime();
  const activeMajorIncident = lastIncident?.severity === 'Major' && lastIncident?.incident_type === 'ACCIDENT' ? lastIncident : null;

  return (
    <div className="flex flex-col gap-6 max-w-7xl mx-auto h-full">
      {/* Urgent Banner */}
      {activeMajorIncident ? (
        <div className="bg-rose-500/10 border border-rose-500 rounded-lg p-4 flex items-center justify-between shadow-[0_0_15px_rgba(244,63,94,0.15)] animate-pulse">
          <div className="flex items-center gap-3 text-rose-500">
            <AlertTriangle size={24} />
            <h2 className="text-xl font-bold tracking-wider">URGENT: INCOMING {activeMajorIncident.incident_type}</h2>
          </div>
          <div className="bg-rose-500/20 text-rose-400 border border-rose-500 px-4 py-1.5 rounded-sm font-bold tracking-widest text-sm">
            CODE RED
          </div>
        </div>
      ) : (
        <div className="bg-emerald-500/10 border border-emerald-500/50 rounded-lg p-4 flex items-center justify-between">
          <div className="flex items-center gap-3 text-emerald-500">
            <AlertTriangle size={24} className="opacity-50" />
            <h2 className="text-xl font-bold tracking-wider">ALL CLEAR: NO MAJOR INCIDENTS</h2>
          </div>
          <div className="bg-emerald-500/20 text-emerald-400 border border-emerald-500 px-4 py-1.5 rounded-sm font-bold tracking-widest text-sm">
            STANDBY
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 flex-1 min-h-[500px]">
        
        {/* Left Column - Incident Details & Map */}
        <div className="lg:col-span-2 flex flex-col gap-6">
          
          {/* Incident Overview Card */}
          {activeMajorIncident ? (
            <div className="bg-dark-panel border border-rose-500/50 rounded-lg p-6 flex flex-col gap-6 relative overflow-hidden">
              <div className="absolute top-0 left-0 w-1 h-full bg-rose-500"></div>
              <div className="flex justify-between items-start">
                <div>
                  <h3 className="text-xl font-bold text-white mb-1">{activeMajorIncident ? 'Incoming Major Incident' : 'No Active Incidents'}</h3>
                  <p className="text-slate-400 text-sm">ID: {activeMajorIncident ? `TG-${activeMajorIncident.id}` : 'N/A'}</p>
                </div>
                <span className="bg-rose-500/20 text-rose-400 border border-rose-500/30 px-3 py-1 rounded-full text-xs font-bold flex items-center gap-2">
                  <span className="w-1.5 h-1.5 bg-rose-500 rounded-full animate-pulse"></span> {activeMajorIncident.severity.toUpperCase()} SEVERITY
                </span>
              </div>

              <div className="grid grid-cols-4 gap-4">
                <div className="bg-dark-sidebar border border-dark-border rounded p-3 text-center">
                  <p className="text-xs text-slate-500 font-semibold mb-1">LOCATION</p>
                  <p className="text-white font-medium text-sm">{activeMajorIncident ? activeMajorIncident.camera_id : '---'}</p>
                </div>
                <div className="bg-dark-sidebar border border-amber-500/30 rounded p-3 text-center relative overflow-hidden">
                  <div className="absolute inset-0 bg-amber-500/5"></div>
                  <p className="text-xs text-slate-500 font-semibold mb-1 relative z-10">EST. ETA</p>
                  <p className="text-amber-400 font-bold text-xl relative z-10">8 MINS</p>
                </div>
                <div className="bg-dark-sidebar border border-dark-border rounded p-3 text-center">
                  <p className="text-xs text-slate-500 font-semibold mb-1">VEHICLES INVOLVED</p>
                  <p className="text-rose-400 font-bold text-xl">{activeMajorIncident ? activeMajorIncident.vehicle_count : '0'}</p>
                </div>
                <div className="bg-dark-sidebar border border-dark-border rounded p-3 text-center">
                  <p className="text-xs text-slate-500 font-semibold mb-1">REQ. TEAMS</p>
                  <p className="text-white font-medium text-sm">Trauma, Ortho</p>
                </div>
              </div>

              <div className="flex gap-4 mt-2">
                <button className="flex-1 bg-indigo-500 hover:bg-indigo-600 text-white font-bold py-3 rounded transition-colors">
                  Accept Alert
                </button>
                <button className="flex-1 bg-dark-sidebar hover:bg-slate-800 border border-dark-border text-slate-300 font-bold py-3 rounded transition-colors">
                  Ambulance Dispatched
                </button>
                <button className="flex-1 bg-dark-sidebar hover:bg-slate-800 border border-dark-border text-slate-300 font-bold py-3 rounded transition-colors">
                  Emergency Room Ready
                </button>
              </div>
            </div>
          ) : (
            <div className="bg-dark-panel border border-dark-border rounded-lg p-6 flex flex-col justify-center items-center h-[280px] text-slate-500">
              <CheckCircle size={48} className="text-emerald-500/20 mb-4" />
              <p className="font-semibold text-lg text-slate-400">No Active Emergency Responses</p>
              <p className="text-sm">Standby for incoming dispatches from TrafficGuard AI</p>
            </div>
          )}

          {/* Live Routing Map */}
          <div className="bg-dark-panel border border-dark-border rounded-lg flex-1 flex flex-col overflow-hidden relative min-h-[300px]">
            <div className="absolute top-0 left-0 w-full p-4 flex justify-between items-center z-[400] bg-gradient-to-b from-dark-panel/90 to-transparent pointer-events-none">
              <h3 className="text-white font-semibold flex items-center gap-2 pointer-events-auto">
                Live Routing: {activeMajorIncident ? activeMajorIncident.camera_id : 'Standby'} to City Hospital
              </h3>
              <span className="bg-dark-sidebar border border-dark-border text-slate-300 text-xs px-3 py-1 rounded font-semibold pointer-events-auto">
                TRAFFIC: CLEAR
              </span>
            </div>
            
            <div className="flex-1 relative z-0">
              <MapContainer 
                center={[44.4268, 26.1025]} 
                zoom={14} 
                style={{ height: '100%', width: '100%', background: '#121621' }}
                zoomControl={false}
              >
                <TileLayer
                  url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
                />
                {/* Mock Route */}
                <Polyline positions={[[44.4368, 26.0925], [44.4268, 26.1025]]} color="#f43f5e" weight={4} dashArray="8, 8" />
              </MapContainer>
            </div>
          </div>
        </div>

        {/* Right Column - Resources */}
        <div className="flex flex-col gap-6">
          
          {/* Bed Availability */}
          <div className="bg-dark-panel border border-dark-border rounded-lg p-6">
            <h3 className="text-white font-semibold flex items-center gap-2 mb-6">
              <Bed size={20} className="text-indigo-400" /> Bed Availability
            </h3>
            
            <div className="space-y-6">
              <div>
                <div className="flex justify-between text-xs font-bold tracking-wider mb-2">
                  <span className="text-slate-300">TRAUMA / ICU</span>
                  <span className="text-rose-400">2 / 10 AVAILABLE</span>
                </div>
                <div className="h-2 w-full bg-slate-800 rounded-full overflow-hidden flex">
                  <div className="h-full bg-rose-400 rounded-full" style={{width: '20%'}}></div>
                </div>
              </div>
              
              <div>
                <div className="flex justify-between text-xs font-bold tracking-wider mb-2">
                  <span className="text-slate-300">SURGERY WARD</span>
                  <span className="text-amber-400">5 / 15 AVAILABLE</span>
                </div>
                <div className="h-2 w-full bg-slate-800 rounded-full overflow-hidden flex">
                  <div className="h-full bg-amber-400 rounded-full" style={{width: '33%'}}></div>
                </div>
              </div>
              
              <div>
                <div className="flex justify-between text-xs font-bold tracking-wider mb-2">
                  <span className="text-slate-300">GENERAL ADMISSION</span>
                  <span className="text-emerald-400">42 / 100 AVAILABLE</span>
                </div>
                <div className="h-2 w-full bg-slate-800 rounded-full overflow-hidden flex">
                  <div className="h-full bg-emerald-400 rounded-full" style={{width: '42%'}}></div>
                </div>
              </div>
            </div>
          </div>


        </div>
      </div>
    </div>
  );
};

export default Hospitals;
