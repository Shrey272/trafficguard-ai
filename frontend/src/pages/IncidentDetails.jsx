import React from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { ArrowLeft, Download, CheckCircle, ShieldAlert, Hourglass } from 'lucide-react';
import CameraFeed from '../components/ui/CameraFeed';
import { MapContainer, TileLayer, Marker, Popup, Circle } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';

const IncidentDetails = () => {
  const navigate = useNavigate();
  const { id } = useParams(); // Using the ID from URL if needed

  return (
    <div className="flex flex-col gap-6 max-w-7xl mx-auto h-full pb-10">
      
      {/* Header */}
      <div>
        <button 
          onClick={() => navigate('/incidents')}
          className="flex items-center gap-2 text-slate-400 hover:text-white transition-colors text-sm mb-4"
        >
          <ArrowLeft size={16} /> Back to Incidents list
        </button>
        <div className="flex justify-between items-end">
          <div>
            <h2 className="text-2xl font-bold text-white mb-1">NH-48 Junction Incident Details</h2>
            <p className="text-slate-400 text-sm">ID: #TRF-99201 • Logged: 10:42 AM</p>
          </div>
          <button className="bg-dark-sidebar border border-dark-border text-slate-300 px-4 py-2 rounded text-sm hover:bg-slate-800 transition-colors flex items-center gap-2">
             Export Log
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Main Camera Feed */}
        <div className="lg:col-span-2">
          <CameraFeed 
            id="CAM-NH48-02" 
            name="NH-48 Junction" 
            type="accident" 
            focus={true}
            imgSrc="/cam_highway.jpg"
            overlayData={[
              { label: "VEHICLE 1 (0V)", x: "35%", y: "45%", w: "30%", h: "20%", color: "red" }
            ]}
          >
             <div className="absolute bottom-4 left-4 bg-black/60 text-slate-300 text-sm px-3 py-1 font-mono tracking-widest border-l-2 border-indigo-500">
                AI Confidence: 94%
             </div>
             <div className="absolute bottom-4 right-4 text-right text-[10px] text-slate-300/80 uppercase font-mono tracking-widest space-y-1">
                <div>INCIDENT STATUS: <span className="text-amber-400">ACTIVE</span></div>
                <div>UNITS RESPONDING: <span className="text-white">POLICE, FIRE</span></div>
                <div>TRAFFIC IMPACT: <span className="text-rose-400">HIGH</span></div>
             </div>
          </CameraFeed>
        </div>

        {/* Sidebar Parameters */}
        <div className="flex flex-col gap-6">
          <div className="bg-dark-panel border border-dark-border rounded-lg p-5">
            <h3 className="text-white font-semibold mb-4">Incident Parameters</h3>
            
            <div className="grid grid-cols-2 gap-4 mb-6">
              <div className="bg-dark-sidebar border border-dark-border rounded p-3">
                <p className="text-xs text-slate-500 font-semibold mb-1">Severity</p>
                <p className="text-rose-400 font-bold flex items-center gap-1.5 text-sm"><ShieldAlert size={14}/> MAJOR</p>
              </div>
              <div className="bg-dark-sidebar border border-dark-border rounded p-3">
                <p className="text-xs text-slate-500 font-semibold mb-1">Vehicles Involved</p>
                <p className="text-white font-medium text-sm">3 detected</p>
              </div>
              <div className="bg-dark-sidebar border border-dark-border rounded p-3">
                <p className="text-xs text-slate-500 font-semibold mb-1">Road Blockage</p>
                <p className="text-amber-400 font-bold text-sm">HIGH</p>
              </div>
              <div className="bg-dark-sidebar border border-dark-border rounded p-3">
                <p className="text-xs text-slate-500 font-semibold mb-1">AI Confidence</p>
                <p className="text-white font-medium text-sm">94.2%</p>
              </div>
            </div>

            <div className="bg-dark-sidebar border border-dark-border rounded p-4 mb-6">
              <p className="text-xs text-slate-500 font-semibold mb-2">Current Status</p>
              <div className="text-amber-400 font-bold flex items-center gap-2 text-lg">
                <Hourglass size={20} /> Awaiting Response
              </div>
            </div>

            <div className="space-y-3">
              <button className="w-full bg-indigo-500/20 text-indigo-400 border border-indigo-500/30 hover:bg-indigo-500/30 py-3 rounded font-bold transition-colors shadow-[0_0_15px_rgba(99,102,241,0.15)]">
                Acknowledge
              </button>
              <button className="w-full bg-dark-sidebar border border-dark-border hover:bg-slate-800 text-white py-3 rounded font-bold transition-colors">
                Mark Response Sent
              </button>
              <button className="w-full bg-dark-sidebar border border-dark-border hover:bg-slate-800 text-white py-3 rounded font-bold transition-colors">
                Resolve Incident
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Spatial Context Map */}
      <div className="bg-dark-panel border border-dark-border rounded-lg p-5">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-white font-semibold">Spatial Context</h3>
          <span className="text-slate-500 text-xs tracking-widest font-mono">LAT: 34.0522 • LNG: -118.2437</span>
        </div>
        <div className="h-[400px] rounded-lg overflow-hidden relative border border-dark-border/50">
          <MapContainer 
            center={[44.4268, 26.1025]} 
            zoom={15} 
            style={{ height: '100%', width: '100%', background: '#121621' }}
            zoomControl={false}
          >
            <TileLayer
              url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
            />
            {/* Mock Incident Marker */}
            <Circle center={[44.4268, 26.1025]} radius={300} pathOptions={{ color: '#f43f5e', fillColor: '#f43f5e', fillOpacity: 0.2 }} />
          </MapContainer>
        </div>
      </div>

    </div>
  );
};

export default IncidentDetails;
