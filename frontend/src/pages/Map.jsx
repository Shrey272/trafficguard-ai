import React, { useState, useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup, useMap } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { Plus, Minus, Focus, Navigation, Video, AlertTriangle, Shield, CheckCircle2, XCircle, Activity, Layers } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { useRealtime } from '../context/RealtimeContext';
import { useNavigate } from 'react-router-dom';

// Fix leaflet default icon path issues in Vite
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
});

// Custom Status Marker Generator
const createCameraIcon = (status) => {
  let bgColor = 'bg-emerald-500';
  let ringColor = 'ring-emerald-400';
  let iconHtml = '📹';

  if (status === 'CONNECTING') {
    bgColor = 'bg-amber-500';
    ringColor = 'ring-amber-400';
  } else if (status === 'ERROR') {
    bgColor = 'bg-rose-500';
    ringColor = 'ring-rose-400';
    iconHtml = '⚠️';
  } else if (status === 'OFFLINE' || status === 'DISABLED') {
    bgColor = 'bg-slate-600';
    ringColor = 'ring-slate-500';
  }

  return L.divIcon({
    className: 'custom-camera-marker',
    html: `
      <div class="relative flex items-center justify-center">
        <div class="w-8 h-8 rounded-full ${bgColor} flex items-center justify-center text-white text-xs font-bold shadow-lg ring-2 ${ringColor} ring-offset-2 ring-offset-[#121621] transition-transform hover:scale-110">
          ${iconHtml}
        </div>
        ${status === 'ONLINE' ? '<span class="absolute -top-1 -right-1 flex h-3 w-3"><span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span><span class="relative inline-flex rounded-full h-3 w-3 bg-emerald-500"></span></span>' : ''}
      </div>
    `,
    iconSize: [32, 32],
    iconAnchor: [16, 16],
    popupAnchor: [0, -18]
  });
};

// Map center setter helper
function ChangeView({ center, zoom }) {
  const map = useMap();
  map.setView(center, zoom);
  return null;
}

const MapView = () => {
  const { authFetch } = useAuth();
  const { incidents, cameraHealthMap } = useRealtime();
  const navigate = useNavigate();

  const [cameras, setCameras] = useState([]);
  const [mapCenter, setMapCenter] = useState([21.1838, 72.8223]);
  const [zoomLevel, setZoomLevel] = useState(13);
  const [showCameras, setShowCameras] = useState(true);
  const [showIncidents, setShowIncidents] = useState(true);
  const [selectedCamera, setSelectedCamera] = useState(null);

  useEffect(() => {
    authFetch('/api/cameras')
      .then(res => res.ok ? res.json() : [])
      .then(data => {
        if (Array.isArray(data)) {
          setCameras(data);
        }
      })
      .catch(err => console.error("Error fetching cameras for GIS:", err));
  }, []);

  const enrichedCameras = cameras.map(cam => {
    const live = cameraHealthMap[cam.id] || cameraHealthMap[cam.camera_code];
    return {
      ...cam,
      status: live?.status || cam.status,
      fps: live?.fps !== undefined ? live?.fps : cam.fps
    };
  });

  const focusLocation = (lat, lng) => {
    setMapCenter([lat, lng]);
    setZoomLevel(16);
  };

  return (
    <div className="flex h-full gap-4 relative -m-4 md:-m-6">
      {/* Map Canvas */}
      <div className="flex-1 relative z-0">
        <MapContainer 
          center={mapCenter} 
          zoom={zoomLevel} 
          style={{ height: '100%', width: '100%', background: '#121621' }}
          zoomControl={false}
        >
          <ChangeView center={mapCenter} zoom={zoomLevel} />
          <TileLayer
            url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'
          />

          {/* CCTV Camera Markers */}
          {showCameras && enrichedCameras.map(cam => {
            if (!cam.latitude || !cam.longitude) return null;
            return (
              <Marker
                key={cam.id}
                position={[cam.latitude, cam.longitude]}
                icon={createCameraIcon(cam.status)}
              >
                <Popup className="custom-popup">
                  <div className="p-3 bg-dark-panel text-white rounded-lg min-w-[220px] font-sans">
                    <div className="flex items-center justify-between gap-2 border-b border-dark-border pb-2 mb-2">
                      <div className="flex items-center gap-1.5 font-bold text-sm text-blue-400">
                        <Video size={15} />
                        <span>{cam.camera_code}</span>
                      </div>
                      <span className={`text-[10px] px-2 py-0.5 rounded font-bold uppercase ${
                        cam.status === 'ONLINE' ? 'bg-emerald-500/20 text-emerald-400' :
                        cam.status === 'CONNECTING' ? 'bg-amber-500/20 text-amber-400' :
                        cam.status === 'ERROR' ? 'bg-rose-500/20 text-rose-400' :
                        'bg-slate-800 text-slate-400'
                      }`}>
                        {cam.status}
                      </span>
                    </div>

                    <p className="font-medium text-xs text-white mb-1">{cam.name}</p>
                    <p className="text-[11px] text-slate-400 mb-2">{cam.location_name}</p>

                    <div className="space-y-1 text-[11px] text-slate-300 border-t border-dark-border pt-2 mb-3">
                      <div className="flex justify-between">
                        <span className="text-slate-400">Department:</span>
                        <span>{cam.department}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-slate-400">Source:</span>
                        <span className="font-mono text-indigo-400">{cam.source_type}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-slate-400">Active Incidents:</span>
                        <span className="font-bold text-rose-400">{cam.incident_count || 0}</span>
                      </div>
                    </div>

                    <div className="flex gap-2">
                      <button
                        onClick={() => navigate('/cameras')}
                        className="flex-1 bg-blue-600 hover:bg-blue-500 text-white text-xs py-1.5 rounded text-center transition-colors font-medium"
                      >
                        View Feed
                      </button>
                      <button
                        onClick={() => navigate('/cameras/manage')}
                        className="flex-1 bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs py-1.5 rounded text-center transition-colors font-medium"
                      >
                        Manage
                      </button>
                    </div>
                  </div>
                </Popup>
              </Marker>
            );
          })}
        </MapContainer>

        {/* Custom Map Controls Overlay */}
        <div className="absolute top-4 left-4 z-[400] flex flex-col gap-3">
          {/* Zoom buttons */}
          <div className="bg-dark-panel border border-dark-border rounded-lg shadow-lg flex flex-col w-48">
            <div className="flex justify-around border-b border-dark-border p-2">
              <button 
                onClick={() => setZoomLevel(prev => Math.min(prev + 1, 18))} 
                className="text-white hover:bg-slate-800 p-2 rounded transition-colors"
                title="Zoom In"
              >
                <Plus size={18} />
              </button>
              <button 
                onClick={() => setZoomLevel(prev => Math.max(prev - 1, 10))} 
                className="text-white hover:bg-slate-800 p-2 rounded transition-colors"
                title="Zoom Out"
              >
                <Minus size={18} />
              </button>
            </div>

            {/* Layer Toggles */}
            <div className="p-3 border-b border-dark-border space-y-2">
              <div className="flex items-center justify-between text-xs text-slate-300">
                <span className="flex items-center gap-1.5"><Video size={13} className="text-blue-400" /> CCTV Cameras</span>
                <input 
                  type="checkbox" 
                  checked={showCameras} 
                  onChange={e => setShowCameras(e.target.checked)}
                  className="rounded text-blue-600 bg-dark-sidebar border-dark-border cursor-pointer"
                />
              </div>
            </div>

            {/* Map Legend */}
            <div className="p-3">
              <h4 className="text-[10px] font-semibold text-slate-400 mb-2 tracking-widest uppercase">GIS CAMERA STATUS</h4>
              <ul className="space-y-2 text-xs text-slate-300">
                <li className="flex items-center gap-2.5">
                  <span className="w-2.5 h-2.5 rounded-full bg-emerald-500 ring-2 ring-emerald-500/30"></span> 
                  <span>Online RTSP</span>
                </li>
                <li className="flex items-center gap-2.5">
                  <span className="w-2.5 h-2.5 rounded-full bg-amber-500 ring-2 ring-amber-500/30"></span> 
                  <span>Connecting / Retry</span>
                </li>
                <li className="flex items-center gap-2.5">
                  <span className="w-2.5 h-2.5 rounded-full bg-rose-500 ring-2 ring-rose-500/30"></span> 
                  <span>Stream Error</span>
                </li>
                <li className="flex items-center gap-2.5 text-slate-400">
                  <span className="w-2.5 h-2.5 rounded-full bg-slate-600"></span> 
                  <span>Offline / Disabled</span>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </div>

      {/* Right Sidebar - Active Incidents & CCTV Focus */}
      <div className="w-80 bg-dark-sidebar border-l border-dark-border z-[400] h-full overflow-y-auto flex flex-col shadow-2xl absolute right-0 top-0 lg:relative">
        <div className="p-4 border-b border-dark-border flex justify-between items-center bg-dark-sidebar/95 sticky top-0 backdrop-blur-sm">
          <h3 className="text-rose-400 font-semibold flex items-center gap-2 text-sm">
            <AlertTriangle size={18} /> Live Incidents & Feeds
          </h3>
          <span className="bg-rose-500/20 text-rose-400 border border-rose-500/30 text-xs px-2 py-0.5 rounded font-bold">
            {incidents.length} ACTIVE
          </span>
        </div>

        <div className="p-4 space-y-3">
          {incidents.length === 0 ? (
            <p className="text-xs text-slate-400 text-center py-6">No active incidents reported.</p>
          ) : (
            incidents.slice(0, 10).map((inc) => (
              <div key={inc.id} className="bg-dark-panel border border-dark-border rounded-lg p-3 hover:border-slate-600 transition-colors">
                <div className="flex justify-between items-start mb-1.5">
                  <span className={`text-[10px] font-bold tracking-wider px-2 py-0.5 rounded ${
                    inc.severity === 'Major' ? 'bg-rose-500/20 text-rose-400 border border-rose-500/30' :
                    inc.severity === 'Moderate' ? 'bg-amber-500/20 text-amber-400 border border-amber-500/30' :
                    'bg-blue-500/20 text-blue-400 border border-blue-500/30'
                  }`}>
                    {inc.incident_type} • {inc.severity}
                  </span>
                  <span className="text-[10px] text-slate-400 font-mono">
                    {inc.timestamp ? new Date(inc.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : ''}
                  </span>
                </div>
                
                <h4 className="text-white text-xs font-semibold mb-1">{inc.camera_id}</h4>
                <p className="text-[11px] text-slate-400 mb-2.5 line-clamp-2">{inc.description || 'Automated AI Detection'}</p>
                
                <div className="flex gap-2">
                  <button 
                    onClick={() => {
                      if (inc.latitude && inc.longitude) {
                        focusLocation(inc.latitude, inc.longitude);
                      }
                    }}
                    className="flex-1 bg-slate-800 hover:bg-slate-700 text-white text-[11px] py-1 rounded flex items-center justify-center gap-1 transition-colors"
                  >
                    <Focus size={12} /> Focus
                  </button>
                  <button 
                    onClick={() => navigate('/cameras')}
                    className="flex-1 bg-indigo-600/20 hover:bg-indigo-600/30 text-indigo-400 border border-indigo-500/30 text-[11px] py-1 rounded flex items-center justify-center gap-1 transition-colors"
                  >
                    <Video size={12} /> Live Feed
                  </button>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
};

export default MapView;
